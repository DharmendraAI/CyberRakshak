from datetime import datetime,timezone

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime

from .database import Base


class FraudCategory(Base):
    __tablename__ = "fraud_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)


class FraudCase(Base):
    __tablename__ = "fraud_cases"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    keywords = Column(Text, nullable=True)

    description = Column(Text, nullable=False)
    how_it_happens = Column(Text, nullable=True)
    warning_signs = Column(Text, nullable=True)
    prevention = Column(Text, nullable=True)
    what_to_do = Column(Text, nullable=True)

    risk_level = Column(String(20), default="Medium")
    active = Column(Boolean, default=True)


class FraudHistory(Base):
    __tablename__ = "fraud_history"

    id = Column(Integer, primary_key=True, index=True)

    message = Column(Text, nullable=False)

    matched_fraud = Column(String(200), nullable=True)

    risk_level = Column(String(20), nullable=False)

    confidence = Column(Integer, default=0, nullable=False)

    score = Column(Integer, default=0, nullable=False)

    matched_keywords = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )