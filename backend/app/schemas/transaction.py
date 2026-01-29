from pydantic import BaseModel
from datetime import datetime

class TransactionRequest(BaseModel):
    user_id: int
    amount: float
    timestamp: datetime
    device_id: int
    location: int

class TransactionResponse(BaseModel):
    risk_score: float
    risk_level: str
    explanation: str