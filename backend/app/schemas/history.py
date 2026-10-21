from datetime import datetime
from pydantic import BaseModel


class HistoryResponse(BaseModel):
    id: int
    message: str
    matched_fraud: str | None = None
    risk_level: str
    confidence: int
    score: int
    matched_keywords: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True