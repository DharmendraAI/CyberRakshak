from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..schemas.fraud import (
    FraudCreate,
    FraudResponse,
    FraudUpdate,
    FraudMatchRequest,
    FraudMatchResponse,
    FraudAnalysisResponse
)
from ..services import fraud_service


router = APIRouter(
    prefix="/api/v1/frauds",
    tags=["Frauds"]
)


# =========================
# DATABASE SESSION
# =========================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================
# CREATE FRAUD
# POST /api/v1/frauds/
# =========================

@router.post(
    "/",
    response_model=FraudResponse,
    status_code=201
)
def create_fraud(
    fraud: FraudCreate,
    db: Session = Depends(get_db)
):
    return fraud_service.create_fraud(
        db,
        fraud
    )


# =========================
# GET ALL FRAUDS
# GET /api/v1/frauds/
# =========================

@router.get(
    "/",
    response_model=List[FraudResponse]
)
def get_all_frauds(
    db: Session = Depends(get_db)
):
    return fraud_service.get_all_frauds(db)


# =========================
# SEARCH & FILTER
# GET /api/v1/frauds/search
# =========================

@router.get(
    "/search",
    response_model=List[FraudResponse]
)
def search_frauds(
    search: Optional[str] = Query(
        default=None,
        description="Search by fraud name, category, or description"
    ),
    category: Optional[str] = Query(
        default=None,
        description="Filter by fraud category"
    ),
    risk_level: Optional[str] = Query(
        default=None,
        description="Filter by risk level: Low, Medium, High"
    ),
    db: Session = Depends(get_db)
):
    return fraud_service.search_frauds(
        db=db,
        search=search,
        category=category,
        risk_level=risk_level
    )


# =========================
# FRAUD MATCHING
# POST /api/v1/frauds/match
# IMPORTANT:
# This must be BEFORE /{fraud_id}
# =========================

@router.post(
    "/match",
    response_model=FraudMatchResponse
)
def match_fraud(
    request: FraudMatchRequest,
    db: Session = Depends(get_db)
):
    return fraud_service.match_fraud_cases(
        db=db,
        message=request.message
    )

@router.post(
    "/analyze",
    response_model=FraudAnalysisResponse
)
def analyze_fraud(
    request: FraudMatchRequest,
    db: Session = Depends(get_db)
):
    return fraud_service.analyze_fraud_message(
        db=db,
        message=request.message
    )

# =========================
# GET FRAUD BY ID
# GET /api/v1/frauds/{fraud_id}
# =========================

@router.get(
    "/{fraud_id}",
    response_model=FraudResponse
)
def get_fraud(
    fraud_id: int,
    db: Session = Depends(get_db)
):
    fraud = fraud_service.get_fraud_by_id(
        db,
        fraud_id
    )

    if fraud is None:
        raise HTTPException(
            status_code=404,
            detail="Fraud not found"
        )

    return fraud


# =========================
# UPDATE FRAUD
# PUT /api/v1/frauds/{fraud_id}
# =========================

@router.put(
    "/{fraud_id}",
    response_model=FraudResponse
)
def update_fraud(
    fraud_id: int,
    fraud_data: FraudUpdate,
    db: Session = Depends(get_db)
):
    updated_fraud = fraud_service.update_fraud(
        db,
        fraud_id,
        fraud_data
    )

    if updated_fraud is None:
        raise HTTPException(
            status_code=404,
            detail="Fraud not found"
        )

    return updated_fraud


# =========================
# DELETE FRAUD
# DELETE /api/v1/frauds/{fraud_id}
# =========================

@router.delete(
    "/{fraud_id}"
)
def delete_fraud(
    fraud_id: int,
    db: Session = Depends(get_db)
):
    deleted_fraud = fraud_service.delete_fraud(
        db,
        fraud_id
    )

    if deleted_fraud is None:
        raise HTTPException(
            status_code=404,
            detail="Fraud not found"
        )

    return {
        "message": "Fraud deleted successfully",
        "id": fraud_id
    }