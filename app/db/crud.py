"""CRUD operations for review records and users."""

import json
import logging
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ReviewRecord

logger = logging.getLogger(__name__)


async def create_review(
    session: AsyncSession,
    review_id: str,
    code: str,
    code_hash: str,
    language: str,
    score: float,
    clean_code_score: float,
    readability_score: float,
    maintainability_score: float,
    security_score: float,
    ml_quality_score: float,
    issue_count: int,
    security_flag_count: int,
    ml_quality_label: str | None,
    ml_confidence: float | None,
    result_json: dict,
    user_id: str | None = None,
    version: int = 1,
) -> ReviewRecord:
    record = ReviewRecord(
        id=review_id,
        code=code,
        code_hash=code_hash,
        language=language,
        score=score,
        clean_code_score=clean_code_score,
        readability_score=readability_score,
        maintainability_score=maintainability_score,
        security_score=security_score,
        ml_quality_score=ml_quality_score,
        issue_count=issue_count,
        security_flag_count=security_flag_count,
        ml_quality_label=ml_quality_label,
        ml_confidence=ml_confidence,
        result_json=json.dumps(result_json),
        user_id=user_id,
        version=version,
        reviewed_at=datetime.utcnow(),
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    logger.info("Review created: id=%s score=%.1f", review_id, score)
    return record


async def get_review(session: AsyncSession, review_id: str) -> ReviewRecord | None:
    result = await session.execute(select(ReviewRecord).where(ReviewRecord.id == review_id))
    return result.scalar_one_or_none()


async def list_reviews(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    user_id: str | None = None,
) -> tuple[list[ReviewRecord], int]:
    query = select(ReviewRecord)
    count_query = select(func.count(ReviewRecord.id))

    if user_id is not None:
        query = query.where(ReviewRecord.user_id == user_id)
        count_query = count_query.where(ReviewRecord.user_id == user_id)

    count_result = await session.execute(count_query)
    total = count_result.scalar_one()

    result = await session.execute(
        query.order_by(ReviewRecord.reviewed_at.desc()).offset(skip).limit(limit)
    )
    records = list(result.scalars().all())
    return records, total


async def get_review_versions(
    session: AsyncSession,
    code_hash: str,
) -> list[ReviewRecord]:
    """Get all review versions for code with the same hash."""
    result = await session.execute(
        select(ReviewRecord)
        .where(ReviewRecord.code_hash == code_hash)
        .order_by(ReviewRecord.reviewed_at.desc())
    )
    return list(result.scalars().all())


async def get_next_version(session: AsyncSession, code_hash: str) -> int:
    """Get the next version number for a code hash."""
    result = await session.execute(
        select(func.max(ReviewRecord.version)).where(
            ReviewRecord.code_hash == code_hash
        )
    )
    current_max = result.scalar_one_or_none()
    return (current_max or 0) + 1
