from pydantic import BaseModel
from datetime import datetime
from typing import List


class TransactionRequest(BaseModel):
    user_id: int
    transaction_type: str   # payment / transfer / cashout / deposit
    amount: float
    timestamp: datetime
    device_id: str          # matches your CSV (device_1, device_2, etc.)
    location: str           # IN, US, UK, etc.


class TransactionResponse(BaseModel):
    risk_score: float
    risk_level: str
    risk_factors: List[str]
    explanation: str