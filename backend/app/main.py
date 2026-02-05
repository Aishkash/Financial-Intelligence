from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import pandas as pd
import joblib

from backend.app.rag.rag_explainer import RAGExplainer

# ---------------------------
# App setup
# ---------------------------
app = FastAPI(title="AI Transaction Risk Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Load artifacts ONCE
# ---------------------------
DATA_PATH = "data/processed/transactions_with_features.csv"
MODEL_PATH = "backend/app/models/risk_model.pkl"

historical_df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])
model = joblib.load(MODEL_PATH)
rag = RAGExplainer()

# ---------------------------
# Schemas
# ---------------------------
class TransactionRequest(BaseModel):
    user_id: int
    transaction_type: str
    amount: float
    timestamp: datetime
    device_id: str
    location: str


class TransactionResponse(BaseModel):
    risk_score: float
    risk_level: str
    risk_factors: list[str]
    context_signals: list[str]
    explanation: str


# ---------------------------
# Helpers
# ---------------------------
def normalize(value: str) -> str:
    return str(value).strip().lower()


# ---------------------------
# Feature builder (INFERENCE SAFE)
# ---------------------------
def build_features(txn: TransactionRequest):
    user_history = historical_df[
        historical_df["user_id"] == txn.user_id
    ].sort_values("timestamp")

    # Defaults
    if user_history.empty:
        user_avg = txn.amount
        user_std = 1.0
        time_since_last = 0.0
        known_devices = set()
        known_locations = set()
    else:
        user_avg = user_history["amount"].mean()
        user_std = user_history["amount"].std() or 1.0
        last_ts = user_history.iloc[-1]["timestamp"]
        time_since_last = (txn.timestamp - last_ts).total_seconds()

        known_devices = set(user_history["device_id"].apply(normalize))
        known_locations = set(user_history["location"].apply(normalize))

    incoming_device = normalize(txn.device_id)
    incoming_location = normalize(txn.location)

    is_new_device = incoming_device not in known_devices
    
    location_counts = (
        user_history["location"]
        .apply(normalize)
        .value_counts(normalize=True)
    )

    location_freq = location_counts.get(incoming_location, 0.0)

    is_new_location = location_freq < 0.10

    # --- REQUIRED FEATURES ---
    hour = txn.timestamp.hour
    day_of_week = txn.timestamp.weekday()
    amount_zscore = (txn.amount - user_avg) / user_std

    X = pd.DataFrame([{
        "hour": hour,
        "day_of_week": day_of_week,
        "time_since_last_txn": time_since_last,
        "amount_zscore": amount_zscore,
        "user_avg_amount": user_avg,
        "user_std_amount": user_std,
    }])

    return X, is_new_device, is_new_location


# ---------------------------
# Risk factor extraction
# ---------------------------
def extract_risk_factors(X: pd.DataFrame) -> list[str]:
    factors = []

    if abs(X["amount_zscore"].iloc[0]) > 3:
        factors.append("Unusually large transaction compared to user's history")

    if X["time_since_last_txn"].iloc[0] < 60:
        factors.append("Rapid succession of transactions")

    if X["hour"].iloc[0] < 5:
        factors.append("Transaction at an unusual hour for this user")

    return factors


# ---------------------------
# API endpoint
# ---------------------------
@app.post("/analyze", response_model=TransactionResponse)



def analyze_transaction(txn: TransactionRequest):

    # 1. Build features
    X, is_new_device, is_new_location = build_features(txn)

    # 2. Base model prediction
    risk_score = float(model.predict_proba(X)[0][1])

    # 3. Policy-based risk adjustments
    if is_new_device:
        risk_score += 0.10   # device novelty risk

    if is_new_location:
        risk_score += 0.15   # location novelty risk (stronger)

    # Cap risk score
    risk_score = min(risk_score, 1.0)

    # 4. Risk level
    if risk_score > 0.7:
        risk_level = "HIGH"
    elif risk_score > 0.4:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # 5. Interpretable ML-based risk factors
    risk_factors = extract_risk_factors(X)

    # 6. Contextual (behavioral) signals
    context_signals = []

    if is_new_device:
        context_signals.append("New device observed")

    if is_new_location:
        context_signals.append("Unusual transaction location for this user")

    # 7. Explanation
    if risk_factors or context_signals:
        try:
            explanation = rag.explain(risk_factors + context_signals)
        except Exception:
            explanation = (
                "This transaction shows deviations from the user's historical "
                "behavior that may require attention."
            )
    else:
        explanation = (
            "This transaction aligns well with the user's historical spending "
            "patterns and behavior."
        )

    return TransactionResponse(
        risk_score=round(risk_score, 3),
        risk_level=risk_level,
        risk_factors=risk_factors,
        context_signals=context_signals,
        explanation=explanation,
    )