"""FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import history, review
from app.auth import routes as auth_routes
from app.db.database import engine, init_db
from app.logging_config import setup_logging

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await init_db()
    yield
    await engine.dispose()


app = FastAPI(
    title="AI Code Reviewer",
    description="Production-grade AI-powered code review system that analyzes code "
    "for issues, suggests improvements, and scores code quality across "
    "5 dimensions: clean code, readability, maintainability, security, and ML quality.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(review.router, prefix="/api/v1", tags=["Review"])
app.include_router(history.router, prefix="/api/v1", tags=["History"])
app.include_router(auth_routes.router, prefix="/api/v1/auth", tags=["Auth"])


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "version": "2.0.0"}
