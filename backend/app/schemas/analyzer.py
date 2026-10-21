from pydantic import BaseModel, Field


class FraudAnalyzeRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=5,
        max_length=5000,
        description="Suspicious SMS, WhatsApp message, email or text"
    )


class FraudIndicator(BaseModel):
    type: str
    description: str
    severity: str


class FraudAnalyzeResponse(BaseModel):
    is_suspicious: bool
    risk_level: str
    matched_fraud: str | None = None
    confidence: int
    indicators: list[FraudIndicator]
    advice: list[str]