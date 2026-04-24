"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/code_reviewer"
    redis_url: str = "redis://localhost:6379/0"
    redis_enabled: bool = False
    redis_ttl_seconds: int = 3600

    # ML
    ml_model_path: str = "app/ml/model/code_quality_model.joblib"
    ml_confidence_threshold: float = 0.6

    # JWT Auth
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    # Scoring weights (dynamic)
    weight_clean_code: float = 0.25
    weight_readability: float = 0.15
    weight_maintainability: float = 0.20
    weight_security: float = 0.25
    weight_ml_quality: float = 0.15

    # Batch review
    max_batch_size: int = 20

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
