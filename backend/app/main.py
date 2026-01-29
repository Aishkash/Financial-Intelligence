from fastapi import FastAPI
import pandas as pd

from backend.app.schemas.transaction import TransactionRequest, TransactionResponse
from backend.app.features.feature_engineering import generate_features
from backend.app.models.risk_model import RiskModel
from backend.app.rag.rag_explainer import RAGExplainer
from dotenv import load_dotenv
load_dotenv()

# rag_explainer = RAGExplainer()
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

    # Risk bucket
    if risk_score > 0.75:
        risk_level = "HIGH"
    elif risk_score > 0.4:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    risk_factors = []

    if df["amount_deviation"].iloc[0] > 3:
        risk_factors.append("High Amount Deviation")

    if df["time_since_last_txn"].iloc[0] < 10:
        risk_factors.append("Rapid Transaction Frequency")

    if df["hour"].iloc[0] < 5:
        risk_factors.append("Unusual Transaction Timing")

    if not risk_factors:
        risk_factors.append("General Anomalous Behavior")

    # 🔒 SAFE RAG CALL
    try:
        rag_explainer = RAGExplainer()
        explanation = rag_explainer.explain(risk_factors)
    except Exception as e:
        explanation = f"Explanation unavailable: {str(e)}"

    return {
        "risk_score": round(float(risk_score), 3),
        "risk_level": risk_level,
        "explanation": explanation
    }