"""CRUD operations for review records."""

import json
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ReviewRecord


async def create_review(
    session: AsyncSession,
    review_id: str,
    code: str,
    language: str,
    score: float,
    issue_count: int,
    security_flag_count: int,
    ml_quality_label: str | None,
    ml_confidence: float | None,
    result_json: dict,
) -> ReviewRecord:
    record = ReviewRecord(
        id=review_id,
        code=code,
        language=language,
        score=score,
        issue_count=issue_count,
        security_flag_count=security_flag_count,
        ml_quality_label=ml_quality_label,
        ml_confidence=ml_confidence,
        result_json=json.dumps(result_json),
        reviewed_at=datetime.utcnow(),
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


async def get_review(session: AsyncSession, review_id: str) -> ReviewRecord | None:
    result = await session.execute(select(ReviewRecord).where(ReviewRecord.id == review_id))
    return result.scalar_one_or_none()


async def list_reviews(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[ReviewRecord], int]:
    count_result = await session.execute(select(func.count(ReviewRecord.id)))
    total = count_result.scalar_one()

    result = await session.execute(
        select(ReviewRecord)
        .order_by(ReviewRecord.reviewed_at.desc())
        .offset(skip)
        .limit(limit)
    )
    records = list(result.scalars().all())
    return records, total
