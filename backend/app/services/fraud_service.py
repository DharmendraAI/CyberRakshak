from sqlalchemy.orm import Session

from ..models import FraudCase, FraudHistory
from ..schemas.fraud import FraudCreate, FraudUpdate

def create_fraud(db: Session, fraud_data: FraudCreate):
    fraud = FraudCase(
        name=fraud_data.name,
        category=fraud_data.category,
        keywords=fraud_data.keywords,
        description=fraud_data.description,
        how_it_happens=fraud_data.how_it_happens,
        warning_signs=fraud_data.warning_signs,
        prevention=fraud_data.prevention,
        what_to_do=fraud_data.what_to_do,
        risk_level=fraud_data.risk_level,
        active=fraud_data.active
    )

    db.add(fraud)
    db.commit()
    db.refresh(fraud)

    return fraud


def get_all_frauds(db: Session):
    return db.query(FraudCase).all()


def get_fraud_by_id(db: Session, fraud_id: int):
    return db.query(FraudCase).filter(
        FraudCase.id == fraud_id
    ).first()


def update_fraud(
    db: Session,
    fraud_id: int,
    fraud_data: FraudUpdate
):
    fraud = get_fraud_by_id(db, fraud_id)

    if not fraud:
        return None

    update_data = fraud_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(fraud, field, value)

    db.commit()
    db.refresh(fraud)

    return fraud


def delete_fraud(db: Session, fraud_id: int):
    fraud = get_fraud_by_id(db, fraud_id)

    if not fraud:
        return None

    db.delete(fraud)
    db.commit()

    return fraud


def search_frauds(
    db: Session,
    search: str | None = None,
    category: str | None = None,
    risk_level: str | None = None
):
    query = db.query(FraudCase)

    if search:
        search_pattern = f"%{search}%"

        query = query.filter(
            (FraudCase.name.ilike(search_pattern)) |
            (FraudCase.description.ilike(search_pattern)) |
            (FraudCase.category.ilike(search_pattern))
        )

    if category:
        query = query.filter(
            FraudCase.category.ilike(category)
        )

    if risk_level:
        query = query.filter(
            FraudCase.risk_level.ilike(risk_level)
        )

    return query.all()

KEYWORD_WEIGHTS = {
    # Critical indicators
    "otp": 3,
    "upi pin": 3,
    "cvv": 3,
    "password": 3,
    "mpin": 3,
    "pin": 3,

    # High importance indicators
    "remote access": 2,
    "screen sharing": 2,
    "video call": 2,
    "kyc": 2,
    "bank account": 2,
    "upi": 2,
    "payment": 2,
    "money transfer": 2,

    # General indicators
    "police": 1,
    "arrest": 1,
    "case": 1,
    "refund": 1,
    "lottery": 1,
    "reward": 1
}

def calculate_final_risk(score: int, confidence: int, fraud_risk: str):
    """
    Calculate final risk level using score,
    confidence and fraud database risk.
    """

    fraud_risk = fraud_risk.lower()

    # Critical indicators
    if score >= 6:
        return "Critical"

    # Strong match
    if confidence >= 60 and fraud_risk == "high":
        return "High"

    # Moderate match
    if score >= 3 or confidence >= 40:
        return "Medium"

    # Weak match
    if score > 0:
        return "Low"

    return "Low"

def match_fraud_cases(db: Session, message: str):
    """
    Match user message against active fraud cases
    using weighted keyword scoring.

    Returns top 3 matching fraud cases.
    """

    normalized_message = message.lower().strip()
    message_words = set(normalized_message.split())

    fraud_cases = db.query(FraudCase).filter(
        FraudCase.active == True
    ).all()

    matches = []

    min_keyword_length = 3

    for fraud in fraud_cases:

        if not fraud.keywords:
            continue

        valid_keywords = [
            keyword.strip().lower()
            for keyword in fraud.keywords.split(",")
            if keyword.strip()
            and len(keyword.strip()) >= min_keyword_length
        ]

        matched_keywords = []
        score = 0

        for keyword in valid_keywords:

            # Multi-word keyword
            if " " in keyword:

                if keyword in normalized_message:
                    matched_keywords.append(keyword)
                    score += KEYWORD_WEIGHTS.get(keyword, 1)

            # Single-word keyword
            else:

                if keyword in message_words:
                    matched_keywords.append(keyword)
                    score += KEYWORD_WEIGHTS.get(keyword, 1)

        if score > 0:

            total_weight = sum(
                KEYWORD_WEIGHTS.get(keyword, 1)
                for keyword in valid_keywords
            )

            confidence = int(
                (score / total_weight) * 100
            ) if total_weight > 0 else 0

            confidence = min(confidence, 100)

            matches.append({
                "matched_fraud": fraud.name,
                "risk_level": fraud.risk_level,
                "confidence": confidence,
                "score": score,
                "matched_keywords": matched_keywords
            })

    # Sort by highest score
    matches.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    # Keep only Top 3
    top_matches = matches[:3]

    # No match
    if not top_matches:
        return {
            "is_suspicious": False,
            "risk_level": "Low",
            "matched_fraud": None,
            "confidence": 0,
            "score": 0,
            "indicators": [],
            "matches": []
        }

    # Best match
    best_match = top_matches[0]

    indicators = []

    for keyword in best_match["matched_keywords"]:

        indicators.append({
            "keyword": keyword,
            "description": (
                f"Message contains a keyword related to "
                f"{best_match['matched_fraud']}."
            ),
            "severity": best_match["risk_level"]
        })

    return {
        "is_suspicious": True,
        "risk_level": best_match["risk_level"],
        "matched_fraud": best_match["matched_fraud"],
        "confidence": best_match["confidence"],
        "score": best_match["score"],
        "indicators": indicators,
        "matches": top_matches
    }
def analyze_fraud_message(db: Session, message: str):
    result = match_fraud_cases(
        db=db,
        message=message
    )

    # --------------------------------
    # No fraud detected
    # --------------------------------
    if not result["is_suspicious"]:

        history = FraudHistory(
            message=message,
            matched_fraud=None,
            risk_level="Low",
            confidence=0,
            score=0,
            matched_keywords=""
        )

        db.add(history)
        db.commit()

        return {
            "message": message,
            "is_suspicious": False,
            "risk_level": "Low",
            "matched_fraud": None,
            "confidence": 0,
            "score": 0,
            "matched_keywords": [],
            "warning_signs": None,
            "prevention": None,
            "what_to_do": None,
            "analysis_summary": (
                "No significant fraud indicators "
                "were detected in the provided message."
            )
        }

    # --------------------------------
    # Get matched fraud
    # --------------------------------
    matched_fraud_name = result["matched_fraud"]

    best_fraud = None

    if matched_fraud_name:
        best_fraud = db.query(FraudCase).filter(
            FraudCase.name == matched_fraud_name,
            FraudCase.active == True
        ).first()

    # --------------------------------
    # Get matched keywords
    # --------------------------------
    matched_keywords = []

    matches = result.get("matches", [])

    if matches:
        matched_keywords = matches[0].get(
            "matched_keywords",
            []
        )

    keyword_text = ", ".join(
        str(keyword)
        for keyword in matched_keywords
    )

    # --------------------------------
    # Fraud not found in database
    # --------------------------------
    if not best_fraud:

        history = FraudHistory(
            message=message,
            matched_fraud=matched_fraud_name,
            risk_level=result["risk_level"],
            confidence=result["confidence"],
            score=result["score"],
            matched_keywords=keyword_text
        )

        db.add(history)
        db.commit()

        return {
            "message": message,
            "is_suspicious": True,
            "risk_level": result["risk_level"],
            "matched_fraud": matched_fraud_name,
            "confidence": result["confidence"],
            "score": result["score"],
            "matched_keywords": matched_keywords,
            "warning_signs": None,
            "prevention": None,
            "what_to_do": None,
            "analysis_summary": (
                f"Potential indicators related to "
                f"{matched_fraud_name} were detected."
            )
        }

    # --------------------------------
    # Normal successful fraud analysis
    # --------------------------------
    analysis_summary = (
        f"This message contains indicators commonly "
        f"associated with {best_fraud.name}. "
        f"Detected indicators: {keyword_text}."
    )

    # --------------------------------
    # Save analysis to history
    # --------------------------------
    history = FraudHistory(
        message=message,
        matched_fraud=best_fraud.name,
        risk_level=result["risk_level"],
        confidence=result["confidence"],
        score=result["score"],
        matched_keywords=keyword_text
    )

    db.add(history)
    db.commit()

    # --------------------------------
    # Return API response
    # --------------------------------
    return {
        "message": message,
        "is_suspicious": True,
        "risk_level": result["risk_level"],
        "matched_fraud": best_fraud.name,
        "confidence": result["confidence"],
        "score": result["score"],
        "matched_keywords": matched_keywords,
        "warning_signs": best_fraud.warning_signs,
        "prevention": best_fraud.prevention,
        "what_to_do": best_fraud.what_to_do,
        "analysis_summary": analysis_summary
    }