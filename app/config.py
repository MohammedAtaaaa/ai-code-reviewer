from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/code_reviewer"
    redis_url: str = "redis://localhost:6379/0"

    # ML
    ml_model_path: str = "app/ml/model/code_quality_model.joblib"
    ml_confidence_threshold: float = 0.6

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
