"""SQLAlchemy models for persisting code reviews."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def _generate_uuid() -> str:
    return str(uuid.uuid4())


class ReviewRecord(Base):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_generate_uuid)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False, default="python")
    score: Mapped[float] = mapped_column(Float, nullable=False)
    issue_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    security_flag_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ml_quality_label: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ml_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    result_json: Mapped[str] = mapped_column(Text, nullable=False)
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<ReviewRecord id={self.id} score={self.score} lang={self.language}>"
