"""Tests for authentication endpoints."""

import os

import pytest
from httpx import ASGITransport, AsyncClient

os.environ["DATABASE_URL"] = "sqlite+aiosqlite://"

from app.db.database import engine, init_db  # noqa: E402
from app.db.models import Base  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "securepass123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["username"] == "testuser"
    assert "user_id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient) -> None:
    payload = {
        "email": "dup@example.com",
        "username": "user1",
        "password": "securepass123",
    }
    await client.post("/api/v1/auth/register", json=payload)
    payload["username"] = "user2"
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "t@e.com", "username": "usr", "password": "short"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "securepass123",
        },
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "securepass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "wp@example.com",
            "username": "wpuser",
            "password": "securepass123",
        },
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "wp@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "anything"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_endpoint_authenticated(client: AsyncClient) -> None:
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "me@example.com",
            "username": "meuser",
            "password": "securepass123",
        },
    )
    token = reg_resp.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["username"] == "meuser"
    assert data["review_count"] == 0


@pytest.mark.asyncio
async def test_me_endpoint_unauthenticated(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_review_with_auth(client: AsyncClient) -> None:
    """Authenticated review should associate review with user."""
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "reviewer@example.com",
            "username": "reviewer",
            "password": "securepass123",
        },
    )
    token = reg_resp.json()["access_token"]

    response = await client.post(
        "/api/v1/review",
        json={"code": "x = 1\nprint(x)\n", "language": "python"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
