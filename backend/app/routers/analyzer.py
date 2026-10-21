from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..schemas.analyzer import (
    FraudAnalyzeRequest,
    FraudAnalyzeResponse
)
from ..services import analyzer_service


router = APIRouter(
    prefix="/api/v1/analyzer",
    tags=["Fraud Analyzer"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post(
    "/analyze",
    response_model=FraudAnalyzeResponse
)
def analyze_message(
    request: FraudAnalyzeRequest,
    db: Session = Depends(get_db)
):
    return analyzer_service.analyze_message(
        db,
        request.message
    )