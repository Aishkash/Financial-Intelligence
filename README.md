# AI-Driven Transaction Risk & Financial Intelligence System

## Overview
This project is a production-style transaction risk monitoring system that combines:

- Machine Learning for real-time risk scoring  
- Behavioral analytics for anomaly detection  
- Retrieval-Augmented Generation (RAG) for explainable decisions  
- FastAPI backend for inference  
- React frontend for live testing  

The system simulates how modern financial institutions detect and explain suspicious transactions.

Synthetic data is used to preserve privacy while maintaining realistic transaction behavior.

---

## Problem Statement

Modern financial systems must not only **detect fraud**, but also **explain why a transaction was flagged**.

This system answers three core questions:

1. Is this transaction risky?
2. How risky is it (numerical score)?
3. Why was it flagged (human-readable explanation)?

---

## Features

- Real-time transaction risk scoring
- Behavioral anomaly detection
- New device & new location detection
- Explainable AI using RAG + LLM
- Risk level classification (LOW / MEDIUM / HIGH)
- Production-style backend architecture
- Interactive frontend dashboard

---

## Tech Stack

### Backend & ML
- Python 3.12
- FastAPI
- Pandas, NumPy
- Scikit-learn
- Joblib
- LangChain
- ChromaDB
- Sentence Transformers
- Groq LLM API

### Frontend
- React (Vite)
- TypeScript
- Fetch API

---

## System Architecture
```
ai-transaction-risk-system/
│
├── backend/
│   └── app/
│       ├── main.py
│       ├── models/
│       │   └── risk_model.pkl
│       ├── rag/
│       │   └── rag_explainer.py
│       ├── features/
│       │   └── feature_engineering.py
│       └── schemas/
│           └── transaction.py
│
├── frontend/
│   └── src/
│       └── App.tsx
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── knowledge/
│   └── vector_store/
│
├── notebooks/
├── .env
├── README.md
└── requirements.txt
```

---




## How the System Works

### Step 1 — Transaction Input
User submits:
- amount  
- timestamp  
- device  
- location  
- transaction type  

### Step 2 — Feature Engineering
Behavioral features generated:
- time of transaction  
- frequency  
- user average spend  
- deviation from history  
- device familiarity  
- location familiarity  

### Step 3 — Risk Model
ML model outputs probability:

```
0.0 → 1.0 risk score
```

Mapped to:
- LOW  
- MEDIUM  
- HIGH  

### Step 4 — Policy Risk Adjustments
Extra risk added if:
- New device detected  
- Unusual location detected  
- Abnormal behavior  

### Step 5 — RAG Explanation Engine
RAG generates human explanation using:
- risk factors
- domain knowledge base
- LLM reasoning

---

## API Endpoints

### Analyze Transaction
```
POST /analyze
```

Request:
```json
{
  "user_id": 10,
  "transaction_type": "payment",
  "amount": 1200,
  "timestamp": "2024-01-12T12:14:00",
  "device_id": "device_10_1",
  "location": "UK"
}
```

Response:
```json
{
  "risk_score": 0.067,
  "risk_level": "LOW",
  "explanation": "This transaction aligns well with the user's historical spending patterns and behavior."
}
```

---

## Run Locally

### 1. Clone repo
```
git clone <your_repo_url>
cd ai-transaction-risk-system
```

### 2. Create virtual environment
```
python -m venv .venv
source .venv/bin/activate
```

### 3. Install backend dependencies
```
pip install -r backend/requirements.txt
```

### 4. Add environment variable
Create `.env` file:
```
GROQ_API_KEY=your_key_here
```

### 5. Start backend
```
uvicorn backend.app.main:app --reload
```

Backend runs on:
```
http://127.0.0.1:8000
```

### 6. Start frontend
```
cd frontend
npm install
npm run dev
```

Frontend runs on:
```
http://localhost:5173
```

---

## Why This Project Matters
This project demonstrates:

- Applied machine learning in finance  
- Explainable AI for risk decisions  
- Real-time API deployment  
- LLM + ML hybrid system design  
- Production-style architecture  

It reflects how modern fintech and banking fraud systems are built.

---

## Future Improvements
- User authentication
- Database logging (PostgreSQL)
- Kafka streaming simulation
- Dashboard analytics
- Cloud deployment (AWS/GCP)
- Model retraining pipeline
- Alerting system

---