# AI Code Reviewer

Production-grade AI-powered code review system that analyzes Python code for issues, suggests improvements, and scores code quality across 5 dimensions.

## Features

- **Multi-Dimensional Scoring** — 5 independent scores (clean code, readability, maintainability, security, ML quality) with detailed explanations
- **Static Analysis** — Detects unused variables/imports, naming convention violations, complex functions, and duplicate code
- **Security Scanner** — Flags `eval`, `exec`, hardcoded secrets, SQL injection, shell injection, insecure crypto, disabled SSL, broad exceptions
- **ML Quality Prediction** — Gradient Boosting classifier predicts good/medium/bad quality with confidence thresholds
- **JWT Authentication** — User accounts with protected endpoints and per-user review history
- **Batch Review** — Review multiple files in a single request
- **Review Versioning** — Track how code quality changes across reviews over time
- **Redis Caching** — Optional caching layer for previously reviewed code
- **Structured Logging** — Consistent logging across all modules

## Tech Stack

- **Backend:** FastAPI, async SQLAlchemy
- **Database:** PostgreSQL (SQLite fallback for dev)
- **ML:** scikit-learn (Gradient Boosting)
- **Auth:** JWT (PyJWT + bcrypt)
- **Cache:** Redis (optional)
- **Testing:** pytest + httpx

## Quick Start

```bash
# Clone and install
git clone https://github.com/MohammedAtaaaa/ai-code-reviewer.git
cd ai-code-reviewer
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure (optional — defaults work for local dev)
cp .env.example .env

# Run with SQLite (no PostgreSQL needed)
DATABASE_URL="sqlite+aiosqlite:///./reviews.db" uvicorn app.main:app --reload

# Or run with Docker Compose (includes PostgreSQL + Redis)
docker compose up --build
```

The API docs are at `http://localhost:8000/docs` (Swagger UI).

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register a new user |
| POST | `/api/v1/auth/login` | Login and receive JWT token |
| GET | `/api/v1/auth/me` | Get current user info (requires auth) |

### Code Review

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/review` | Submit code for review |
| GET | `/api/v1/review/{id}` | Retrieve a specific review |
| POST | `/api/v1/review-batch` | Review multiple files at once |
| GET | `/api/v1/reviews` | List review history |
| GET | `/api/v1/reviews/{id}/history` | Get version history for a review |
| GET | `/health` | Health check |

### Example: Submit a Review

```bash
curl -X POST http://localhost:8000/api/v1/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def f(x):\n    eval(x)\n    password = \"secret\"\n    return x",
    "language": "python"
  }'
```

Response includes:
```json
{
  "id": "uuid",
  "score": 3.2,
  "score_breakdown": {
    "overall": 3.2,
    "clean_code": 6.8,
    "readability": 7.1,
    "maintainability": 8.5,
    "security": 0.0,
    "ml_quality": 2.5,
    "explanations": {
      "security": ["[CRITICAL] dangerous-call-eval: ..."],
      "clean_code": ["2 unused item(s) detected"]
    }
  },
  "issues": [...],
  "security_flags": [...],
  "ml_prediction": {
    "quality_label": "bad",
    "confidence": 0.92,
    "meets_threshold": true
  },
  "summary": "Code Quality: Poor (3.2/10)\n..."
}
```

### Example: Batch Review

```bash
curl -X POST http://localhost:8000/api/v1/review-batch \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"code": "x = 1\nprint(x)", "language": "python"},
      {"code": "def greet(name):\n    return f\"Hi, {name}\"", "language": "python"}
    ]
  }'
```

### Example: Register + Authenticated Review

```bash
# Register
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "dev@example.com", "username": "dev", "password": "securepass123"}' \
  | jq -r '.access_token')

# Submit review with auth
curl -X POST http://localhost:8000/api/v1/review \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"code": "print(\"hello\")", "language": "python"}'
```

## Scoring System

Each review produces 5 independent scores (0–10):

| Dimension | What it measures |
|-----------|-----------------|
| **Clean Code** | Unused vars/imports, duplicates, function structure |
| **Readability** | Naming conventions, comments/docstrings ratio |
| **Maintainability** | Cyclomatic complexity, function size, maintainability index |
| **Security** | Vulnerability patterns, risky calls, hardcoded secrets |
| **ML Quality** | ML model prediction (good/medium/bad with confidence) |

The **overall score** is a weighted blend (configurable via env vars):
- Clean Code: 25%, Security: 25%, Maintainability: 20%, Readability: 15%, ML Quality: 15%

## Configuration

All settings are configurable via environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | PostgreSQL | Database connection string |
| `REDIS_ENABLED` | `false` | Enable Redis caching |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection |
| `JWT_SECRET_KEY` | `change-me-in-production` | JWT signing key |
| `ML_CONFIDENCE_THRESHOLD` | `0.6` | Min ML confidence for reliable predictions |
| `WEIGHT_*` | various | Scoring dimension weights (must sum to 1.0) |
| `MAX_BATCH_SIZE` | `20` | Maximum files per batch request |

## Testing

```bash
source .venv/bin/activate
pytest tests/ -v
```

65 tests covering: API endpoints, authentication, batch review, versioning, scoring, security checks, static analysis, and ML predictions.

## Architecture

```
app/
├── api/
│   ├── routes/          # FastAPI route handlers
│   │   ├── review.py    # Review + batch endpoints
│   │   └── history.py   # History + versioning endpoints
│   └── schemas/         # Pydantic request/response models
├── auth/                # JWT authentication module
│   ├── routes.py        # Register, login, me endpoints
│   ├── utils.py         # Password hashing, JWT encode/decode
│   ├── schemas.py       # Auth request/response models
│   └── dependencies.py  # FastAPI auth dependencies
├── analysis/            # AST-based static analysis
│   ├── unused_vars.py   # Unused variable/import detection
│   ├── naming.py        # PEP 8 naming conventions
│   ├── functions.py     # Function complexity analysis
│   └── duplicates.py    # Duplicate code detection
├── services/
│   ├── analyzer.py      # Analysis orchestrator
│   ├── scorer.py        # Multi-dimensional scoring
│   ├── security_checker.py  # Security vulnerability detection
│   └── complexity.py    # Cyclomatic complexity metrics
├── ml/                  # Machine learning module
│   ├── features.py      # Feature extraction (18 features)
│   ├── train.py         # Model training with synthetic data
│   └── predict.py       # Quality prediction service
├── db/                  # Database layer
│   ├── database.py      # Engine + session management
│   ├── models.py        # SQLAlchemy models (User, ReviewRecord)
│   └── crud.py          # CRUD operations
├── cache.py             # Redis caching layer
├── config.py            # Pydantic settings
├── logging_config.py    # Structured logging setup
└── main.py              # FastAPI app entry point
```

## License

MIT
