from fastapi import FastAPI
import pandas as pd

from backend.app.schemas.transaction import TransactionRequest, TransactionResponse
from backend.app.features.feature_engineering import generate_features
from backend.app.models.risk_model import RiskModel

app = FastAPI(title="AI Transaction Risk System")

# ---- Load and train model on startup ----
df = pd.read_csv("data/processed/transactions_with_features.csv")

feature_cols = [
    "amount",
    "hour",
    "day_of_week",
    "time_since_last_txn",
    "user_avg_amount",
    "user_std_amount",
    "amount_deviation"
]


X = df[feature_cols]
y = df["is_fraud"]

risk_model = RiskModel()
risk_model.train(X, y)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Risk system running"}
    
@app.post("/analyze", response_model=TransactionResponse)
def analyze_transaction(txn: TransactionRequest):

    # Convert input to DataFrame
    df = pd.DataFrame([txn.dict()])

    # Generate features
    df = generate_features(df)

    X = df[[
        "amount",
        "hour",
        "day_of_week",
        "time_since_last_txn",
        "user_avg_amount",
        "user_std_amount",
        "amount_deviation"
    ]]

    # Predict risk
    risk_score = risk_model.predict_risk(X)[0]

    # Simple risk bucket
    if risk_score > 0.75:
        risk_level = "HIGH"
    elif risk_score > 0.4:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return TransactionResponse(
        risk_score=round(float(risk_score), 3),
        risk_level=risk_level
    )