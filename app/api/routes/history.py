"""Review history and versioning endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.review import (
    ReviewHistoryItem,
    ReviewListResponse,
    ReviewVersionItem,
    ReviewVersionsResponse,
)
from app.auth.dependencies import get_current_user
from app.db.crud import get_review, get_review_versions, list_reviews
from app.db.database import get_session
from app.db.models import User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/reviews", response_model=ReviewListResponse)
async def get_review_history(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Max records to return"),
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user),
) -> ReviewListResponse:
    """Retrieve paginated review history. Authenticated users see only their reviews."""
    user_id = user.id if user else None
    records, total = await list_reviews(session, skip=skip, limit=limit, user_id=user_id)

    items = [
        ReviewHistoryItem(
            id=r.id,
            language=r.language,
            score=r.score,
            clean_code_score=r.clean_code_score,
            readability_score=r.readability_score,
            maintainability_score=r.maintainability_score,
            security_score=r.security_score,
            ml_quality_score=r.ml_quality_score,
            issue_count=r.issue_count,
            security_flag_count=r.security_flag_count,
            version=r.version,
            reviewed_at=r.reviewed_at,
            code_snippet=r.code[:200],
        )
        for r in records
    ]

    return ReviewListResponse(total=total, reviews=items)


@router.get("/reviews/{review_id}/history", response_model=ReviewVersionsResponse)
async def get_version_history(
    review_id: str,
    session: AsyncSession = Depends(get_session),
) -> ReviewVersionsResponse:
    """
    Get all versions of reviews for the same code.

    Tracks how the code quality has changed across reviews over time.
    """
    record = await get_review(session, review_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Review not found.")

    versions = await get_review_versions(session, record.code_hash)
    logger.info(
        "Version history for %s: %d versions", review_id, len(versions)
    )

    items = [
        ReviewVersionItem(
            id=v.id,
            score=v.score,
            clean_code_score=v.clean_code_score,
            readability_score=v.readability_score,
            maintainability_score=v.maintainability_score,
            security_score=v.security_score,
            ml_quality_score=v.ml_quality_score,
            issue_count=v.issue_count,
            security_flag_count=v.security_flag_count,
            version=v.version,
            reviewed_at=v.reviewed_at,
        )
        for v in versions
    ]

    return ReviewVersionsResponse(
        code_hash=record.code_hash,
        total_versions=len(items),
        versions=items,
    )
