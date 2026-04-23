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
    score: float = Field(ge=0, le=10, description="Code quality score (0–10)")
    security_flags: list[SecurityFlag] = Field(default_factory=list)
    ml_prediction: MLPrediction | None = None
    complexity_metrics: dict[str, float] = Field(default_factory=dict)
    summary: str = Field(description="Human-readable review summary")
    reviewed_at: datetime = Field(default_factory=datetime.utcnow)


class ReviewHistoryItem(BaseModel):
    id: str
    language: str
    score: float
    issue_count: int
    security_flag_count: int
    reviewed_at: datetime
    code_snippet: str = Field(description="First 200 chars of the submitted code")


class ReviewListResponse(BaseModel):
    total: int
    reviews: list[ReviewHistoryItem]
