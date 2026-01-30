# AI-Driven Transaction Risk & Financial Intelligence System

## Overview

This project implements an **industry-style transaction risk monitoring system** that combines:

- Classical Machine Learning for **risk scoring**
- Behavioral feature engineering for **anomaly detection**
- Retrieval-Augmented Generation (RAG) for **explainable risk decisions**
- A FastAPI backend for **real-time inference**

The system mirrors how **financial institutions detect, score, and explain risky transactions** in production.

> Synthetic data is used to simulate realistic transaction behavior while maintaining data privacy.

---

## Problem Statement

Modern financial systems must not only **detect fraud**, but also **explain why a transaction was flagged**.

This system answers three core questions:

1. Is this transaction risky?
2. How risky is it (numerical score)?
3. Why was it flagged (human-readable explanation)?

---

## System Architecture
```
ai-transaction-risk-system/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point
│   │   │                            # Transaction request → response
│   │   │
│   │   ├── schemas/
│   │   │   └── transaction.py      # API request & response schemas
│   │   │
│   │   ├── features/
│   │   │   └── feature_engineering.py
│   │   │                            # Behavioral feature extraction
│   │   │                            # (time, frequency, deviation)
│   │   │
│   │   ├── models/
│   │   │   └── risk_model.py        # Classical ML risk scoring model
│   │   │                            # Outputs risk probability
│   │   │
│   │   ├── rag/
│   │   │   └── rag_explainer.py     # RAG-based explanation engine
│   │   │                            # LLM + vector store
│   │   │
│   │   └── db/
│   │       └── (optional)           # Future audit / persistence layer
│   │
│   └── requirements.txt             # Backend dependencies
│
├── data/
│   ├── raw/
│   │   └── transactions.csv         # Synthetic raw transaction data
│   │
│   ├── processed/
│   │   └── transactions_with_features.csv
│   │                                # ML-ready dataset
│   │
│   ├── knowledge/
│   │   └── risk_explanations.txt    # Domain knowledge for RAG
│   │
│   └── vector_store/                # ChromaDB embeddings (ignored in git)
│
├── notebooks/
│   ├── 01_generate_data.ipynb       # Data simulation
│   ├── 02_feature_engineering.ipynb # Feature + label creation
│   └── 03_model_training.ipynb      # Model experimentation
│
├── .env                             # Environment variables (GROQ_API_KEY)
├── .gitignore
├── README.md
└── venv/                            # Local virtual environment (not tracked)
```






---

## Data Pipeline

### 1. Synthetic Data Generation

Transactions are synthetically generated to resemble real-world behavior.

Fields include:
- `user_id`
- `amount`
- `timestamp`
- `device_id`
- `location`

Stored at:

---

### 2. Feature Engineering (Behavioral Modeling)

Key engineered features:

- `hour` – time-of-day behavior
- `day_of_week` – weekday vs weekend activity
- `time_since_last_txn` – transaction velocity
- `user_avg_amount` – baseline spending
- `user_std_amount` – spending volatility
- `amount_deviation` – anomaly score

These features model **behavioral deviation**, not just transaction size.

---

### 3. Risk Model

- Classical ML model trained on engineered features
- Outputs a **continuous risk probability**
- Mapped to risk levels:
  - LOW
  - MEDIUM
  - HIGH

Classical ML is intentionally used for:
- Interpretability
- Stability
- Regulatory friendliness

---

## Explainability with RAG

### Why RAG?

Fraud models alone produce numbers.  
Financial systems require **clear, auditable explanations**.

### RAG Flow

1. Identify dominant risk factors:
   - High amount deviation
   - Rapid transaction frequency
   - Unusual transaction timing
2. Pass risk factors to an LLM
3. Generate a human-readable explanation

RAG is used **only for explanation**, not prediction.

---

Get/

```bash
Response:
```json
{
  "status": "ok",
  "message": "Risk system running"
}
```
Analyze Transaction
```bash
POST /analyze
```
Request
```bash
{
  "user_id": 10,
  "amount": 12000,
  "timestamp": "2024-01-12T03:14:00",
  "device_id": 99,
  "location": 20
}
```

Response
```bash
{
  "risk_score": 0.833,
  "risk_level": "HIGH",
  "explanation": "This transaction was flagged due to a significant deviation from the user’s typical spending behavior combined with rapid transaction activity."
}
```

## ⚙️ Tech Stack

### Backend & Machine Learning
- **Python 3.12** – Core programming language
- **FastAPI** – High-performance API framework for real-time inference
- **Pandas / NumPy** – Data manipulation and numerical computation
- **Scikit-learn** – Classical machine learning models for risk scoring
- **Sentence Transformers** – Text embeddings for semantic similarity
- **ChromaDB** – Vector database for retrieval-augmented generation
- **Groq LLM API** – Low-latency large language model inference
- **LangChain** – Lightweight orchestration for RAG pipelines

Running the Project Locally
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Set environment variable
export GROQ_API_KEY=your_api_key_here

# Start FastAPI server
uvicorn backend.app.main:app --reload
```

