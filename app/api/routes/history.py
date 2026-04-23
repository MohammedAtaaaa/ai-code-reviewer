"""Review history endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.review import ReviewHistoryItem, ReviewListResponse
from app.db.crud import list_reviews
from app.db.database import get_session

router = APIRouter()


@router.get("/reviews", response_model=ReviewListResponse)
async def get_review_history(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Max records to return"),
    session: AsyncSession = Depends(get_session),
) -> ReviewListResponse:
    """Retrieve paginated review history."""
    records, total = await list_reviews(session, skip=skip, limit=limit)

    items = [
        ReviewHistoryItem(
            id=r.id,
            language=r.language,
            score=r.score,
            issue_count=r.issue_count,
            security_flag_count=r.security_flag_count,
            reviewed_at=r.reviewed_at,
            code_snippet=r.code[:200],
        )
        for r in records
    ]

    return ReviewListResponse(total=total, reviews=items)
