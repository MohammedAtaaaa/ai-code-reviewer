# AI Code Reviewer

A production-grade, AI-powered code review system that analyzes Python code for quality issues, security vulnerabilities, and code complexity. Combines AST-based static analysis with ML classification to provide comprehensive, human-readable feedback.

## Features

- **Static Code Analysis** — Detects unused variables/imports, naming convention violations, overly complex functions, and duplicate code patterns via Python AST
- **Security Scanning** — Flags dangerous calls (`eval`, `exec`), hardcoded secrets, SQL injection patterns, risky imports (`pickle`, `subprocess`)
- **ML Quality Classification** — Gradient boosting model trained on code features to classify quality as good/medium/bad with confidence scores
- **Cyclomatic Complexity** — Measures code complexity and maintainability index
- **Scoring System** — Combines all signals into a 0–10 score with weighted penalties
- **Review History** — Stores all reviews in PostgreSQL with full retrieval API
- **Human-Readable Feedback** — Generates senior-reviewer-style explanations and actionable suggestions

## Architecture

```
app/
├── api/
│   ├── routes/          # FastAPI endpoint handlers
│   │   ├── review.py    # POST /review, GET /review/{id}
│   │   └── history.py   # GET /reviews (paginated)
│   └── schemas/         # Pydantic request/response models
├── analysis/            # AST-based static analysis
│   ├── unused_vars.py   # Unused variable/import detection
│   ├── naming.py        # PEP 8 naming convention checks
│   ├── functions.py     # Function length, args, nesting depth
│   └── duplicates.py    # Structural duplicate detection
├── services/            # Business logic layer
│   ├── analyzer.py      # Orchestrates all analysis passes
│   ├── scorer.py        # Final scoring + summary generation
│   ├── complexity.py    # Cyclomatic complexity & maintainability
│   └── security_checker.py  # Security vulnerability detection
├── ml/                  # Machine learning layer
│   ├── features.py      # Feature extraction from source code
│   ├── train.py         # Model training with synthetic data
│   ├── predict.py       # Prediction service (singleton)
│   └── model/           # Saved model artifacts
├── db/                  # Database layer
│   ├── database.py      # Async SQLAlchemy engine/session
│   ├── models.py        # ORM models
│   └── crud.py          # CRUD operations
├── config.py            # Pydantic settings
└── main.py              # FastAPI app with lifespan
```

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Start everything (app + PostgreSQL + Redis)
docker compose up --build

# API is available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
pip install aiosqlite  # for local SQLite fallback

# 3. Configure environment
cp .env.example .env
# Edit .env — for local dev without PostgreSQL, use:
#   DATABASE_URL=sqlite+aiosqlite:///./reviews.db

# 4. Train the ML model
python scripts/train_model.py

# 5. Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Tests

```bash
pip install pytest pytest-asyncio aiosqlite httpx
pytest tests/ -v
```

## API Reference

### `POST /api/v1/review` — Submit Code for Review

**Request:**
```json
{
  "code": "def f(x):\n    eval(x)\n    password = 'secret'\n    y = 1\n    return x",
  "language": "python"
}
```

**Response:**
```json
{
  "id": "a1b2c3d4-...",
  "issues": [
    {
      "rule": "unused-variable",
      "severity": "warning",
      "line": 4,
      "message": "Unused variable 'y'. Remove it to keep the code clean and avoid confusion.",
      "suggestion": "Remove the unused variable 'y' or prefix with '_' if intentionally unused."
    }
  ],
  "suggestions": [
    "Remove unused variables: y.",
    "Follow PEP 8 naming conventions: snake_case for functions/variables, PascalCase for classes."
  ],
  "score": 3.2,
  "security_flags": [
    {
      "rule": "dangerous-call-eval",
      "severity": "critical",
      "line": 2,
      "message": "eval() executes arbitrary code and is a major security risk.",
      "recommendation": "Avoid using eval(). Use safer alternatives or validate all inputs rigorously."
    },
    {
      "rule": "hardcoded-secret",
      "severity": "critical",
      "line": 3,
      "message": "Possible hardcoded secret detected.",
      "recommendation": "Use environment variables or a secrets manager."
    }
  ],
  "ml_prediction": {
    "quality_label": "bad",
    "confidence": 0.87
  },
  "complexity_metrics": {
    "cyclomatic_complexity": 1,
    "maintainability_index": 62.5,
    "lines_of_code": 5,
    "source_lines_of_code": 5
  },
  "summary": "Code Quality: Poor (3.2/10)\nOverall assessment: This code is concerning.\nFound 4 issue(s) to address.\nSECURITY: 2 critical security issue(s) found — fix these before deploying.",
  "reviewed_at": "2024-01-15T10:30:00"
}
```

### `GET /api/v1/review/{review_id}` — Retrieve a Specific Review

### `GET /api/v1/reviews?skip=0&limit=20` — Paginated Review History

**Response:**
```json
{
  "total": 42,
  "reviews": [
    {
      "id": "a1b2c3d4-...",
      "language": "python",
      "score": 7.5,
      "issue_count": 2,
      "security_flag_count": 0,
      "reviewed_at": "2024-01-15T10:30:00",
      "code_snippet": "def calculate_total(items: ..."
    }
  ]
}
```

### `GET /health` — Health Check

## Analysis Rules

| Rule | Severity | Description |
|------|----------|-------------|
| `unused-variable` | warning | Variable defined but never used |
| `unused-import` | warning | Import never referenced |
| `naming-convention` | info | PEP 8 naming violation |
| `function-lines` | warning | Function exceeds 50 lines |
| `function-arguments` | warning | Function has more than 5 parameters |
| `function-nesting_depth` | warning | Nesting deeper than 4 levels |
| `duplicate-code` | warning | Structurally similar functions (≥80%) |
| `dangerous-call-eval` | critical | Use of `eval()` |
| `dangerous-call-exec` | critical | Use of `exec()` |
| `hardcoded-secret` | critical | Passwords/keys/tokens in source |
| `sql-injection` | critical | String interpolation in SQL queries |
| `shell-injection` | critical | `subprocess` with `shell=True` |
| `risky-import-pickle` | warning | Importing pickle (deserialization risk) |

## ML Model

The classifier uses **Gradient Boosting** trained on 18 code features:

- Lines of code, SLOC, blank/comment ratios
- Function count, class count, import count
- Cyclomatic complexity, max nesting depth
- Average/max function length and argument count
- Docstring coverage ratio
- Naming violation ratio
- Halstead volume estimate

The model outputs `good` / `medium` / `bad` with confidence scores, which are blended (30% weight) with rule-based analysis for the final score.

## Configuration

All settings via environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | Database connection |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis for caching (optional) |
| `APP_ENV` | `development` | Environment mode |
| `APP_PORT` | `8000` | Server port |

## License

MIT
