"""Tests for the batch review endpoint."""

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
async def test_batch_review_success(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/review-batch",
        json={
            "items": [
                {"code": "x = 1\nprint(x)\n", "language": "python"},
                {
                    "code": "def greet(name: str) -> str:\n    return f'Hello, {name}'\n",
                    "language": "python",
                },
            ]
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "reviews" in data
    assert "summary" in data
    assert len(data["reviews"]) == 2
    assert data["summary"]["total_files"] == 2
    assert 0 <= data["summary"]["average_score"] <= 10


@pytest.mark.asyncio
async def test_batch_review_with_summary(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/review-batch",
        json={
            "items": [
                {"code": "print('a')\n", "language": "python"},
                {"code": "print('b')\n", "language": "python"},
                {"code": "print('c')\n", "language": "python"},
            ]
        },
    )
    assert response.status_code == 200
    data = response.json()
    summary = data["summary"]
    assert summary["total_files"] == 3
    assert summary["min_score"] <= summary["average_score"] <= summary["max_score"]
    assert isinstance(summary["total_issues"], int)


@pytest.mark.asyncio
async def test_batch_review_empty_items(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/review-batch",
        json={"items": []},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_batch_review_mixed_languages(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/review-batch",
        json={
            "items": [
                {"code": "x = 1\n", "language": "python"},
                {"code": "let x = 1;", "language": "javascript"},
            ]
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["reviews"]) == 2
    # JS review should have no ML prediction
    js_review = data["reviews"][1]
    assert js_review["ml_prediction"] is None
