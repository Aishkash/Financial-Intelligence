from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib

# ---------------------------
# App setup
# ---------------------------
app = FastAPI(title="AI Transaction Risk Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # frontend later
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Load artifacts ONCE
# ---------------------------
DATA_PATH = "data/processed/transactions_with_features.csv"
MODEL_PATH = "backend/app/models/risk_model.pkl"

historical_df = pd.read_csv(DATA_PATH)
model = joblib.load(MODEL_PATH)

FEATURES = [
    "hour",
    "day_of_week",
    "time_since_last_txn",
    "amount_zscore",
    "user_avg_amount",
    "user_std_amount"
]

# ---------------------------
# Request / Response schema
# ---------------------------
class TransactionRequest(BaseModel):
    user_id: int
    transaction_type: str
    amount: float
    timestamp: str
    device_id: str
    location: str

class TransactionResponse(BaseModel):
    risk_score: float
    risk_level: str
    risk_factors: list[str]
    explanation: str

# ---------------------------
# Helper: compute features for ONE txn
# ---------------------------
def build_features(txn: TransactionRequest) -> pd.DataFrame:
    df = historical_df[historical_df["user_id"] == txn.user_id].copy()

    new_row = {
        "user_id": txn.user_id,
        "transaction_type": txn.transaction_type,
        "amount": txn.amount,
        "timestamp": pd.to_datetime(txn.timestamp),
        "device_id": txn.device_id,
        "location": txn.location,
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    # Time features
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek

    df["time_since_last_txn"] = (
        df.groupby("user_id")["timestamp"]
        .diff()
        .dt.total_seconds()
        .fillna(0)
    )

    # Amount stats
    stats = df.groupby("user_id")["amount"].agg(["mean", "std"]).reset_index()
    stats.columns = ["user_id", "user_avg_amount", "user_std_amount"]
    df = df.merge(stats, on="user_id", how="left")

    df["amount_zscore"] = (
        df["amount"] - df["user_avg_amount"]
    ) / (df["user_std_amount"] + 1)

    return df.tail(1)[FEATURES]

# ---------------------------
# Risk explanation logic
# ---------------------------
def explain(txn_df: pd.DataFrame) -> tuple[list[str], str]:
    factors = []

    if txn_df["amount_zscore"].iloc[0] > 3:
        factors.append("Unusually large transaction compared to user's history")

    if txn_df["time_since_last_txn"].iloc[0] < 60:
        factors.append("Rapid transaction frequency")

    if txn_df["hour"].iloc[0] < 5:
        factors.append("Transaction at unusual hour for this user")

    if not factors:
        explanation = (
            "This transaction aligns with the user's historical behavior "
            "in terms of amount, timing, and frequency."
        )
    else:
        explanation = " | ".join(factors)

    return factors, explanation

# ---------------------------
# API endpoint
# ---------------------------
@app.post("/analyze", response_model=TransactionResponse)
def analyze_transaction(txn: TransactionRequest):
    X = build_features(txn)

    risk_score = float(model.predict_proba(X)[0][1])

    if risk_score > 0.7:
        level = "HIGH"
    elif risk_score > 0.4:
        level = "MEDIUM"
    else:
        level = "LOW"

    factors, explanation = explain(X)

    return {
        "risk_score": round(risk_score, 3),
        "risk_level": level,
        "risk_factors": factors,
        "explanation": explanation,
    }