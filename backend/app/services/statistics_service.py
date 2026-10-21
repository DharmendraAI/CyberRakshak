from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import FraudHistory


def get_dashboard_statistics(db: Session):

    # Total analyses
    total_analyses = (
        db.query(FraudHistory)
        .count()
    )

    # Suspicious cases
    suspicious_cases = (
        db.query(FraudHistory)
        .filter(
            FraudHistory.score > 0
        )
        .count()
    )

    # Risk-level counts
    critical_cases = (
        db.query(FraudHistory)
        .filter(
            FraudHistory.risk_level.ilike("Critical")
        )
        .count()
    )

    high_cases = (
        db.query(FraudHistory)
        .filter(
            FraudHistory.risk_level.ilike("High")
        )
        .count()
    )

    medium_cases = (
        db.query(FraudHistory)
        .filter(
            FraudHistory.risk_level.ilike("Medium")
        )
        .count()
    )

    low_cases = (
        db.query(FraudHistory)
        .filter(
            FraudHistory.risk_level.ilike("Low")
        )
        .count()
    )

    # Suspicious percentage
    if total_analyses > 0:
        suspicious_percentage = round(
            (suspicious_cases / total_analyses) * 100,
            2
        )
    else:
        suspicious_percentage = 0.0

    # Most detected fraud
    top_fraud = (
        db.query(
            FraudHistory.matched_fraud,
            func.count(FraudHistory.id).label("count")
        )
        .filter(
            FraudHistory.matched_fraud.isnot(None)
        )
        .group_by(
            FraudHistory.matched_fraud
        )
        .order_by(
            func.count(FraudHistory.id).desc()
        )
        .first()
    )

    top_detected_fraud = None
    top_detected_fraud_count = 0

    if top_fraud:
        top_detected_fraud = top_fraud[0]
        top_detected_fraud_count = top_fraud[1]

    return {
        "total_analyses": total_analyses,
        "suspicious_cases": suspicious_cases,

        "critical_cases": critical_cases,
        "high_cases": high_cases,
        "medium_cases": medium_cases,
        "low_cases": low_cases,

        "suspicious_percentage": suspicious_percentage,

        "top_detected_fraud": top_detected_fraud,
        "top_detected_fraud_count": top_detected_fraud_count
    }
def get_fraud_distribution(db: Session):
    """Return fraud-wise detection counts for dashboard charts."""

    results = (
        db.query(
            FraudHistory.matched_fraud,
            func.count(FraudHistory.id).label("count")
        )
        .filter(
            FraudHistory.matched_fraud.isnot(None)
        )
        .group_by(
            FraudHistory.matched_fraud
        )
        .order_by(
            func.count(FraudHistory.id).desc()
        )
        .all()
    )

    return [
        {
            "fraud_name": fraud_name,
            "count": count
        }
        for fraud_name, count in results
    ]
def get_risk_distribution(db: Session):
    """Return risk-level counts for dashboard charts."""

    results = (
        db.query(
            FraudHistory.risk_level,
            func.count(FraudHistory.id).label("count")
        )
        .group_by(
            FraudHistory.risk_level
        )
        .order_by(
            FraudHistory.risk_level
        )
        .all()
    )

    return [
        {
            "risk_level": risk_level,
            "count": count
        }
        for risk_level, count in results
    ]