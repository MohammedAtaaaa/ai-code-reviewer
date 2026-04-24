"""Pydantic schemas for code review requests and responses."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class CodeIssue(BaseModel):
    rule: str = Field(description="Rule identifier, e.g. 'unused-variable'")
    severity: Severity
    line: int | None = Field(default=None, description="Line number where the issue occurs")
    message: str = Field(description="Human-readable explanation of the issue")
    suggestion: str | None = Field(default=None, description="How to fix the issue")


class SecurityFlag(BaseModel):
    rule: str = Field(description="Security rule identifier")
    severity: Severity
    line: int | None = None
    message: str
    recommendation: str


class MLPrediction(BaseModel):
    quality_label: str = Field(description="Predicted quality: good, medium, or bad")
    confidence: float = Field(description="Model confidence (0.0–1.0)")
    probabilities: dict[str, float] = Field(
        default_factory=dict,
        description="Per-class probabilities",
    )
    meets_threshold: bool = Field(
        default=True,
        description="Whether confidence meets the reliability threshold",
    )


class ScoreBreakdownResponse(BaseModel):
    overall: float = Field(ge=0, le=10, description="Weighted overall score")
    clean_code: float = Field(ge=0, le=10, description="Clean code score")
    readability: float = Field(ge=0, le=10, description="Readability score")
    maintainability: float = Field(ge=0, le=10, description="Maintainability score")
    security: float = Field(ge=0, le=10, description="Security score")
    ml_quality: float = Field(ge=0, le=10, description="ML quality score")
    explanations: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Per-dimension explanations",
    )


class ReviewRequest(BaseModel):
    code: str = Field(description="Source code to review", min_length=1)
    language: str = Field(default="python", description="Programming language")

    model_config = {
        "json_schema_extra": {
            "examples": [{"code": "x = 1\nprint(x)", "language": "python"}]
        }
    }


class ReviewResponse(BaseModel):
    id: str = Field(description="Unique review identifier")
    issues: list[CodeIssue] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    score: float = Field(ge=0, le=10, description="Overall code quality score (0–10)")
    score_breakdown: ScoreBreakdownResponse = Field(
        description="Detailed score breakdown by dimension"
    )
    security_flags: list[SecurityFlag] = Field(default_factory=list)
    ml_prediction: MLPrediction | None = None
    complexity_metrics: dict[str, float] = Field(default_factory=dict)
    summary: str = Field(description="Human-readable review summary")
    version: int = Field(default=1, description="Review version number")
    reviewed_at: datetime = Field(default_factory=datetime.utcnow)
    cached: bool = Field(default=False, description="Whether result was served from cache")


class ReviewHistoryItem(BaseModel):
    id: str
    language: str
    score: float
    clean_code_score: float = 0.0
    readability_score: float = 0.0
    maintainability_score: float = 0.0
    security_score: float = 0.0
    ml_quality_score: float = 0.0
    issue_count: int
    security_flag_count: int
    version: int = 1
    reviewed_at: datetime
    code_snippet: str = Field(description="First 200 chars of the submitted code")


class ReviewListResponse(BaseModel):
    total: int
    reviews: list[ReviewHistoryItem]


class ReviewVersionItem(BaseModel):
    id: str
    score: float
    clean_code_score: float = 0.0
    readability_score: float = 0.0
    maintainability_score: float = 0.0
    security_score: float = 0.0
    ml_quality_score: float = 0.0
    issue_count: int
    security_flag_count: int
    version: int
    reviewed_at: datetime


class ReviewVersionsResponse(BaseModel):
    code_hash: str
    total_versions: int
    versions: list[ReviewVersionItem]


# Batch review schemas
class BatchReviewItem(BaseModel):
    code: str = Field(description="Source code to review", min_length=1)
    language: str = Field(default="python")
    filename: str | None = Field(default=None, description="Optional filename for context")


class BatchReviewRequest(BaseModel):
    items: list[BatchReviewItem] = Field(
        min_length=1, description="List of code snippets to review"
    )


class BatchReviewSummary(BaseModel):
    total_files: int
    average_score: float
    min_score: float
    max_score: float
    total_issues: int
    total_security_flags: int


class BatchReviewResponse(BaseModel):
    reviews: list[ReviewResponse]
    summary: BatchReviewSummary
