"""Authentication endpoints."""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.auth.utils import create_access_token, hash_password, verify_password
from app.db.database import get_session
from app.db.models import User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    """Register a new user account."""
    existing = await session.execute(select(User).where(User.email == request.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered.",
        )

    existing_name = await session.execute(
        select(User).where(User.username == request.username)
    )
    if existing_name.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken.",
        )

    user = User(
        id=str(uuid.uuid4()),
        email=request.email,
        username=request.username,
        password_hash=hash_password(request.password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    token = create_access_token(user.id, user.email)
    logger.info("User registered: %s (%s)", user.username, user.email)
    return TokenResponse(
        access_token=token, user_id=user.id, username=user.username
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    """Authenticate and receive a JWT token."""
    result = await session.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = create_access_token(user.id, user.email)
    logger.info("User logged in: %s", user.email)
    return TokenResponse(
        access_token=token, user_id=user.id, username=user.username
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(
        __import__("app.auth.dependencies", fromlist=["require_user"]).require_user
    ),
) -> UserResponse:
    """Get current authenticated user info."""
    from sqlalchemy import func

    from app.db.models import ReviewRecord

    count_result = await session.execute(
        select(func.count(ReviewRecord.id)).where(ReviewRecord.user_id == user.id)
    )
    review_count = count_result.scalar_one()

    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        review_count=review_count,
    )
