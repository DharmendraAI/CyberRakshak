from typing import List

from ..schemas.history import HistoryResponse
from ..models import FraudHistory
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..schemas.statistics import (
    FraudDistribution,
    RiskDistribution
)
from ..services import statistics_service


router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["Dashboard Analytics"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get(
    "/fraud-distribution",
    response_model=List[FraudDistribution]
)
def fraud_distribution(
    db: Session = Depends(get_db)
):
    return statistics_service.get_fraud_distribution(db)


@router.get(
    "/risk-distribution",
    response_model=List[RiskDistribution]
)
def risk_distribution(
    db: Session = Depends(get_db)
):
    return statistics_service.get_risk_distribution(db)
@router.get(
    "/recent-activity",
    response_model=List[HistoryResponse]
)
def get_recent_activity(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    limit = max(1, min(limit, 50))

    records = (
        db.query(FraudHistory)
        .order_by(FraudHistory.created_at.desc())
        .limit(limit)
        .all()
    )

    return records