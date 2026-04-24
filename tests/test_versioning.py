"""Tests for review versioning system."""

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
async def test_version_increments(client: AsyncClient) -> None:
    """Reviewing the same code multiple times should increment version."""
    code = "x = 1\nprint(x)\n"

    resp1 = await client.post(
        "/api/v1/review", json={"code": code, "language": "python"}
    )
    assert resp1.status_code == 200
    assert resp1.json()["version"] == 1

    resp2 = await client.post(
        "/api/v1/review", json={"code": code, "language": "python"}
    )
    assert resp2.status_code == 200
    assert resp2.json()["version"] == 2


@pytest.mark.asyncio
async def test_version_history_endpoint(client: AsyncClient) -> None:
    """GET /reviews/{id}/history should return all versions."""
    code = "x = 1\nprint(x)\n"

    resp1 = await client.post(
        "/api/v1/review", json={"code": code, "language": "python"}
    )
    review_id = resp1.json()["id"]

    # Submit same code again
    await client.post("/api/v1/review", json={"code": code, "language": "python"})

    history_resp = await client.get(f"/api/v1/reviews/{review_id}/history")
    assert history_resp.status_code == 200
    data = history_resp.json()
    assert data["total_versions"] == 2
    assert len(data["versions"]) == 2
    assert "code_hash" in data


@pytest.mark.asyncio
async def test_version_history_nonexistent(client: AsyncClient) -> None:
    response = await client.get("/api/v1/reviews/nonexistent-id/history")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_different_code_separate_versions(client: AsyncClient) -> None:
    """Different code should have separate version tracks."""
    resp1 = await client.post(
        "/api/v1/review", json={"code": "x = 1\n", "language": "python"}
    )
    resp2 = await client.post(
        "/api/v1/review", json={"code": "y = 2\n", "language": "python"}
    )
    assert resp1.json()["version"] == 1
    assert resp2.json()["version"] == 1
