import re

from sqlalchemy.orm import Session

from ..models import FraudCase


# =================================================
# TEXT NORMALIZATION
# =================================================

def normalize_text(text: str) -> str:
    """
    Normalize user message for reliable matching.
    """

    text = text.lower()

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =================================================
# FRAUD KEYWORD SCORE
# =================================================

def keyword_match_score(keyword: str, text: str):
    """
    Calculate score for one fraud keyword.

    Longer phrases receive higher scores because
    they are generally more specific.
    """

    keyword = normalize_text(keyword)

    if not keyword:
        return 0

    pattern = r"\b" + re.escape(keyword) + r"\b"

    if not re.search(pattern, text):
        return 0

    word_count = len(keyword.split())

    if word_count >= 4:
        return 12

    if word_count == 3:
        return 10

    if word_count == 2:
        return 7

    return 3


# =================================================
# RISK INDICATOR DETECTION
# =================================================

def detect_risk_indicators(text: str):
    """
    Detect common social-engineering and cyber-fraud
    warning indicators in a message.
    """

    indicators = []

    # ---------------------------------------------
    # Urgency
    # ---------------------------------------------

    urgency_keywords = [
        "urgent",
        "immediately",
        "immediate",
        "right now",
        "act now",
        "within 24 hours",
        "today",
        "as soon as possible"
    ]

    matched = [
        keyword
        for keyword in urgency_keywords
        if re.search(
            r"\b" + re.escape(keyword) + r"\b",
            text
        )
    ]

    if matched:
        indicators.append({
            "type": "Urgency",
            "description": (
                "The message creates pressure to take "
                "immediate action."
            ),
            "severity": "Medium"
        })

    # ---------------------------------------------
    # Threat
    # ---------------------------------------------

    threat_keywords = [
        "account blocked",
        "account suspended",
        "account will be blocked",
        "legal action",
        "arrest",
        "penalty",
        "fine",
        "police case",
        "criminal case"
    ]

    matched = [
        keyword
        for keyword in threat_keywords
        if keyword in text
    ]

    if matched:
        indicators.append({
            "type": "Threat",
            "description": (
                "The message uses threats or consequences "
                "to pressure the recipient."
            ),
            "severity": "High"
        })

    # ---------------------------------------------
    # OTP Request
    # ---------------------------------------------

    otp_keywords = [
        "otp",
        "one time password",
        "verification code",
        "security code"
    ]

    matched = [
        keyword
        for keyword in otp_keywords
        if keyword in text
    ]

    if matched:
        indicators.append({
            "type": "OTP Request",
            "description": (
                "The message mentions an OTP or "
                "verification code."
            ),
            "severity": "High"
        })

    # ---------------------------------------------
    # PIN / CVV
    # ---------------------------------------------

    credential_keywords = [
        "upi pin",
        "pin",
        "cvv",
        "password",
        "passcode"
    ]

    matched = [
        keyword
        for keyword in credential_keywords
        if re.search(
            r"\b" + re.escape(keyword) + r"\b",
            text
        )
    ]

    if matched:
        indicators.append({
            "type": "Sensitive Credential",
            "description": (
                "The message mentions sensitive "
                "authentication information."
            ),
            "severity": "High"
        })

    # ---------------------------------------------
    # Payment Request
    # ---------------------------------------------

    payment_keywords = [
        "send money",
        "transfer money",
        "make payment",
        "pay now",
        "payment",
        "transfer",
        "upi payment",
        "collect request"
    ]

    matched = [
        keyword
        for keyword in payment_keywords
        if keyword in text
    ]

    if matched:
        indicators.append({
            "type": "Payment Request",
            "description": (
                "The message contains a request or "
                "instruction related to payment."
            ),
            "severity": "High"
        })

    # ---------------------------------------------
    # Suspicious Link
    # ---------------------------------------------

    url_pattern = r"https?://\S+|www\.\S+"

    if re.search(url_pattern, text):

        indicators.append({
            "type": "Suspicious Link",
            "description": (
                "The message contains a web link. "
                "Verify the destination through an "
                "official source before opening it."
            ),
            "severity": "High"
        })

    # ---------------------------------------------
    # Authority Impersonation
    # ---------------------------------------------

    authority_keywords = [
        "police officer",
        "police",
        "rbi officer",
        "bank officer",
        "government officer",
        "income tax officer",
        "customs officer"
    ]

    matched = [
        keyword
        for keyword in authority_keywords
        if keyword in text
    ]

    if matched:
        indicators.append({
            "type": "Authority Claim",
            "description": (
                "The message claims to represent a "
                "government, police or financial authority."
            ),
            "severity": "High"
        })

    return indicators


# =================================================
# MAIN ANALYZER
# =================================================

def analyze_message(
    db: Session,
    message: str
):
    text = normalize_text(message)

    indicators = []
    matched_frauds = []

    # =================================================
    # GET ACTIVE FRAUD PATTERNS
    # =================================================

    frauds = (
        db.query(FraudCase)
        .filter(FraudCase.active.is_(True))
        .all()
    )

    # =================================================
    # FRAUD KEYWORD MATCHING
    # =================================================

    for fraud in frauds:

        if not fraud.keywords:
            continue

        keywords = [
            keyword.strip()
            for keyword in fraud.keywords.split(",")
            if keyword.strip()
        ]

        matched_keywords = []
        fraud_score = 0

        for keyword in keywords:

            score = keyword_match_score(
                keyword,
                text
            )

            if score > 0:

                matched_keywords.append({
                    "keyword": keyword,
                    "score": score
                })

                fraud_score += score

        if matched_keywords:

            matched_frauds.append({
                "fraud": fraud,
                "keywords": matched_keywords,
                "score": fraud_score
            })

    # =================================================
    # RISK INDICATORS
    # =================================================

    risk_indicators = detect_risk_indicators(text)

    # Add risk indicators to existing indicators

    indicators.extend(risk_indicators)

    # =================================================
    # NO FRAUD DETECTED
    # =================================================

    if not matched_frauds:

        return {
            "is_suspicious": bool(risk_indicators),
            "risk_level": (
                "Medium"
                if risk_indicators
                else "Low"
            ),
            "matched_fraud": None,
            "confidence": 25 if risk_indicators else 10,
            "indicators": indicators,
            "advice": [
                "Do not click suspicious links.",
                "Do not share OTP, PIN, password or CVV.",
                "Verify unexpected messages through official sources."
            ]
        }

    # =================================================
    # SORT BY MATCH SCORE
    # =================================================

    matched_frauds.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    # =================================================
    # PRIMARY FRAUD
    # =================================================

    primary_fraud = matched_frauds[0]

    matched_fraud_name = primary_fraud["fraud"].name

    # =================================================
    # FRAUD RISK
    # =================================================

    risk_priority = {
        "Low": 1,
        "Medium": 2,
        "High": 3
    }

    highest_risk = "Low"

    for item in matched_frauds:

        fraud_risk = item["fraud"].risk_level or "Medium"

        if risk_priority.get(
            fraud_risk,
            2
        ) > risk_priority.get(
            highest_risk,
            1
        ):
            highest_risk = fraud_risk

    # =================================================
    # ADD FRAUD MATCH INDICATORS
    # =================================================

    for item in matched_frauds:

        fraud = item["fraud"]

        matched_keyword_names = [
            keyword_data["keyword"]
            for keyword_data in item["keywords"]
        ]

        indicators.append({
            "type": fraud.name,
            "description": (
                f"Matched keywords: "
                f"{', '.join(matched_keyword_names)}."
            ),
            "severity": fraud.risk_level or "Medium"
        })

    # =================================================
    # CONFIDENCE
    # =================================================

    primary_score = primary_fraud["score"]

    confidence = min(
        95,
        40 + (primary_score * 5)
    )

    # =================================================
    # SAFETY ADVICE
    # =================================================

    advice = [
        "Do not click suspicious links.",
        "Do not share OTP, PIN, password or CVV.",
        "Verify the message through the official website or application.",
        "Do not transfer money because of pressure or urgency."
    ]

    # =================================================
    # FRAUD-SPECIFIC ADVICE
    # =================================================

    for item in matched_frauds:

        fraud = item["fraud"]

        if fraud.prevention:

            advice.append(
                fraud.prevention
            )

    # =================================================
    # REMOVE DUPLICATE ADVICE
    # =================================================

    advice = list(dict.fromkeys(advice))

    # =================================================
    # FINAL RESPONSE
    # =================================================

    return {
        "is_suspicious": True,
        "risk_level": highest_risk,
        "matched_fraud": matched_fraud_name,
        "confidence": confidence,
        "indicators": indicators,
        "advice": advice
    }