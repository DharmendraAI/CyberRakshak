from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..schemas.statistics import DashboardStatistics
from ..services import statistics_service


router = APIRouter(
    prefix="/api/v1/statistics",
    tags=["Dashboard Statistics"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get(
    "/dashboard",
    response_model=DashboardStatistics
)
def get_dashboard_statistics(
    db: Session = Depends(get_db)
):
    return statistics_service.get_dashboard_statistics(db)