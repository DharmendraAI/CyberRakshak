from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import FraudHistory
from ..schemas.history import HistoryResponse


router = APIRouter(
    prefix="/api/v1/history",
    tags=["Fraud History"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------
# GET ALL HISTORY
# Search + Risk Filter + Pagination
# ---------------------------------------------------------

@router.get("/")
def get_history(
    page: int = Query(
        default=1,
        ge=1,
        description="Page number"
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of records per page"
    ),
    risk_level: Optional[str] = Query(
        default=None,
        description="Filter by risk level: Low, Medium, High, Critical"
    ),
    search: Optional[str] = Query(
        default=None,
        description="Search in message or matched fraud"
    ),
    db: Session = Depends(get_db)
):
    query = db.query(FraudHistory)

    # -----------------------------------------
    # Search
    # -----------------------------------------
    if search:
        search_pattern = f"%{search}%"

        query = query.filter(
            (FraudHistory.message.ilike(search_pattern))
            |
            (FraudHistory.matched_fraud.ilike(search_pattern))
        )

    # -----------------------------------------
    # Risk Level Filter
    # -----------------------------------------
    if risk_level:
        query = query.filter(
            FraudHistory.risk_level.ilike(risk_level)
        )

    # -----------------------------------------
    # Total Records
    # -----------------------------------------
    total = query.count()

    # -----------------------------------------
    # Pagination
    # -----------------------------------------
    offset = (page - 1) * limit

    records = (
        query
        .order_by(FraudHistory.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    # -----------------------------------------
    # Total Pages
    # -----------------------------------------
    total_pages = (total + limit - 1) // limit

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "records": records
    }


# ---------------------------------------------------------
# GET HISTORY BY ID
# ---------------------------------------------------------

@router.get(
    "/{history_id}",
    response_model=HistoryResponse
)
def get_history_by_id(
    history_id: int,
    db: Session = Depends(get_db)
):
    history = (
        db.query(FraudHistory)
        .filter(FraudHistory.id == history_id)
        .first()
    )

    if history is None:
        raise HTTPException(
            status_code=404,
            detail="History record not found"
        )

    return history


# ---------------------------------------------------------
# DELETE HISTORY BY ID
# ---------------------------------------------------------

@router.delete("/{history_id}")
def delete_history(
    history_id: int,
    db: Session = Depends(get_db)
):
    history = (
        db.query(FraudHistory)
        .filter(FraudHistory.id == history_id)
        .first()
    )

    if history is None:
        raise HTTPException(
            status_code=404,
            detail="History record not found"
        )

    db.delete(history)
    db.commit()

    return {
        "message": "History deleted successfully",
        "id": history_id
    }