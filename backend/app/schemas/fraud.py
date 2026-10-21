from pydantic import BaseModel, Field
from typing import Optional

class FraudBase(BaseModel):
    name: str = Field(
        ...,
        min_length=3,
        max_length=200
    )

    category: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    keywords: Optional[str] = None

    description: str

    how_it_happens: Optional[str] = None
    warning_signs: Optional[str] = None
    prevention: Optional[str] = None
    what_to_do: Optional[str] = None

    risk_level: str = "Medium"

    active: bool = True


class FraudCreate(FraudBase):
    pass


class FraudUpdate(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=200
    )

    category: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100
    )

    keywords: Optional[str] = None

    description: Optional[str] = None

    how_it_happens: Optional[str] = None
    warning_signs: Optional[str] = None
    prevention: Optional[str] = None
    what_to_do: Optional[str] = None

    risk_level: Optional[str] = None

    active: Optional[bool] = None

class FraudMatchRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=5,
        description="Suspicious message or text provided by the user"
    )

class FraudResponse(FraudBase):
    id: int

    class Config:
        from_attributes = True
class FraudMatchIndicator(BaseModel):
    keyword: str
    description: str
    severity: str



class FraudMatchResult(BaseModel):
    matched_fraud: str
    risk_level: str
    confidence: int
    score: int
    matched_keywords: list[str]


class FraudMatchResponse(BaseModel):
    is_suspicious: bool
    risk_level: str
    matched_fraud: Optional[str] = None
    confidence: int
    score: int
    indicators: list[FraudMatchIndicator]
    matches: list[FraudMatchResult] = Field(default_factory=list)

class FraudAnalysisResponse(BaseModel):
    message: str
    is_suspicious: bool
    risk_level: str
    matched_fraud: Optional[str] = None
    confidence: int
    score: int
    matched_keywords: list[str]
    warning_signs: Optional[str] = None
    prevention: Optional[str] = None
    what_to_do: Optional[str] = None
    analysis_summary: str