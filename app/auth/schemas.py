"""Pydantic schemas for authentication."""

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    email: str = Field(description="User email address")
    username: str = Field(min_length=3, max_length=50, description="Username")
    password: str = Field(min_length=8, description="Password (min 8 chars)")


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    review_count: int = 0
