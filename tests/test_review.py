"""Tests for the review API endpoint."""

# Override database URL before importing app
import os
import textwrap

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
async def test_health_check(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_review_clean_code(client: AsyncClient) -> None:
    code = textwrap.dedent("""\
        def greet(name: str) -> str:
            \"\"\"Return a greeting message.\"\"\"
            return f"Hello, {name}!"
    """)
    response = await client.post(
        "/api/v1/review",
        json={"code": code, "language": "python"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert 0 <= data["score"] <= 10
    assert isinstance(data["issues"], list)
    assert isinstance(data["suggestions"], list)
    assert isinstance(data["security_flags"], list)
    assert "summary" in data
    assert "id" in data


@pytest.mark.asyncio
async def test_review_bad_code(client: AsyncClient) -> None:
    code = textwrap.dedent("""\
        def f(x):
            eval(x)
            password = "secret123"
            y = 1
            z = 2
            return x
    """)
    response = await client.post(
        "/api/v1/review",
        json={"code": code, "language": "python"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["score"] < 8
    assert len(data["security_flags"]) > 0
    assert len(data["issues"]) > 0


@pytest.mark.asyncio
async def test_review_empty_code(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/review",
        json={"code": "", "language": "python"},
    )
    assert response.status_code == 422  # validation error from min_length=1


@pytest.mark.asyncio
async def test_review_history(client: AsyncClient) -> None:
    code = "x = 1\nprint(x)\n"
    await client.post("/api/v1/review", json={"code": code, "language": "python"})

    response = await client.get("/api/v1/reviews")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "reviews" in data
    assert isinstance(data["reviews"], list)


@pytest.mark.asyncio
async def test_review_nonexistent(client: AsyncClient) -> None:
    response = await client.get("/api/v1/review/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_ml_prediction_included(client: AsyncClient) -> None:
    code = textwrap.dedent("""\
        class UserService:
            def get_user(self, user_id: int):
                return self.repo.find(user_id)
    """)
    response = await client.post(
        "/api/v1/review",
        json={"code": code, "language": "python"},
    )
    assert response.status_code == 200
    data = response.json()
    if data["ml_prediction"] is not None:
        assert "quality_label" in data["ml_prediction"]
        assert "confidence" in data["ml_prediction"]
