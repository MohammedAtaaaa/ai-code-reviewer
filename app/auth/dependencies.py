"""Auth dependencies for FastAPI route protection."""

import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.utils import decode_access_token
from app.db.database import get_session
from app.db.models import User

logger = logging.getLogger(__name__)

_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    session: AsyncSession = Depends(get_session),
) -> User | None:
    """Return the authenticated user, or None for anonymous access."""
    if credentials is None:
        return None
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        return None
    from sqlalchemy import select

    result = await session.execute(select(User).where(User.id == payload["sub"]))
    return result.scalar_one_or_none()


async def require_user(
    user: User | None = Depends(get_current_user),
) -> User:
    """Require authentication — raise 401 if not logged in."""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
