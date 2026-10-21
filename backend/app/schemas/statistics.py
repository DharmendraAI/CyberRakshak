from pydantic import BaseModel
from typing import Optional


class DashboardStatistics(BaseModel):
    total_analyses: int
    suspicious_cases: int

    critical_cases: int
    high_cases: int
    medium_cases: int
    low_cases: int

    suspicious_percentage: float

    top_detected_fraud: Optional[str] = None
    top_detected_fraud_count: int = 0


class FraudDistribution(BaseModel):
    fraud_name: str
    count: int


class RiskDistribution(BaseModel):
    risk_level: str
    count: int