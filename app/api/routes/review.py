"""Code review endpoint."""

import contextlib
import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.review import (
    CodeIssue,
    MLPrediction,
    ReviewRequest,
    ReviewResponse,
    SecurityFlag,
    Severity,
)
from app.db.crud import create_review, get_review
from app.db.database import get_session
from app.ml.predict import get_predictor
from app.services.analyzer import CodeAnalyzer
from app.services.scorer import CodeScorer

router = APIRouter()
analyzer = CodeAnalyzer()
scorer = CodeScorer()


@router.post("/review", response_model=ReviewResponse)
async def review_code(
    request: ReviewRequest,
    session: AsyncSession = Depends(get_session),
) -> ReviewResponse:
    """
    Analyze submitted code and return a comprehensive review.

    The review includes:
    - Detected issues (bugs, bad practices, anti-patterns)
    - Improvement suggestions from a senior reviewer perspective
    - A code quality score (0–10)
    - Security warnings for risky patterns
    - ML-based quality prediction with confidence level
    """
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code must not be empty.")

    # Run static analysis
    analysis = analyzer.analyze(request.code, request.language)

    # Run ML prediction
    ml_result = None
    ml_score = None
    if request.language == "python":
        try:
            predictor = get_predictor()
            ml_result = predictor.predict(request.code)
            ml_score = ml_result["score"]
        except Exception:
            pass  # ML is optional — degrade gracefully

    # Compute final score
    code_lines = len(request.code.splitlines())
    score, suggestions = scorer.score(analysis, ml_score=ml_score, code_length=code_lines)

    # Build issue list
    issues: list[CodeIssue] = []

    for item in analysis.unused_items:
        issues.append(
            CodeIssue(
                rule=f"unused-{item.kind}",
                severity=Severity.WARNING,
                line=item.line,
                message=f"Unused {item.kind} '{item.name}'. "
                "Remove it to keep the code clean and avoid confusion.",
                suggestion=f"Remove the unused {item.kind} '{item.name}' "
                "or prefix with '_' if intentionally unused.",
            )
        )

    for ni in analysis.naming_issues:
        issues.append(
            CodeIssue(
                rule="naming-convention",
                severity=Severity.INFO,
                line=ni.line,
                message=ni.message,
                suggestion=f"Rename '{ni.name}' to follow {ni.expected_convention} convention.",
            )
        )

    for fi in analysis.function_issues:
        issues.append(
            CodeIssue(
                rule=f"function-{fi.metric}",
                severity=Severity.WARNING,
                line=fi.line,
                message=fi.message,
                suggestion=f"Refactor '{fi.name}' to reduce {fi.metric} "
                f"(current: {fi.value}, recommended max: {fi.threshold}).",
            )
        )

    for dup in analysis.duplicates:
        issues.append(
            CodeIssue(
                rule="duplicate-code",
                severity=Severity.WARNING,
                line=dup.lines_a[0],
                message=dup.message,
                suggestion="Extract the common logic into a shared helper function.",
            )
        )

    # Security flags
    security_flags: list[SecurityFlag] = []
    for sec in analysis.security_issues:
        security_flags.append(
            SecurityFlag(
                rule=sec.rule,
                severity=Severity(sec.severity),
                line=sec.line,
                message=sec.message,
                recommendation=sec.recommendation,
            )
        )

    # Complexity metrics
    complexity_metrics: dict[str, float] = {}
    if analysis.complexity:
        complexity_metrics = {
            "cyclomatic_complexity": analysis.complexity.cyclomatic_complexity,
            "maintainability_index": analysis.complexity.maintainability_index,
            "lines_of_code": analysis.complexity.loc,
            "source_lines_of_code": analysis.complexity.sloc,
            "comment_ratio": analysis.complexity.comment_ratio,
            "function_count": analysis.complexity.function_count,
            "class_count": analysis.complexity.class_count,
        }

    # ML prediction
    ml_prediction = None
    if ml_result:
        ml_prediction = MLPrediction(
            quality_label=ml_result["quality_label"],
            confidence=ml_result["confidence"],
        )

    # Generate summary
    summary = scorer.generate_summary(score, analysis, suggestions)

    review_id = str(uuid.uuid4())

    response = ReviewResponse(
        id=review_id,
        issues=issues,
        suggestions=suggestions,
        score=score,
        security_flags=security_flags,
        ml_prediction=ml_prediction,
        complexity_metrics=complexity_metrics,
        summary=summary,
    )

    # Persist to database (failure should not break the review response)
    with contextlib.suppress(Exception):
        await create_review(
            session=session,
            review_id=review_id,
            code=request.code,
            language=request.language,
            score=score,
            issue_count=len(issues),
            security_flag_count=len(security_flags),
            ml_quality_label=ml_result["quality_label"] if ml_result else None,
            ml_confidence=ml_result["confidence"] if ml_result else None,
            result_json=response.model_dump(mode="json"),
        )

    return response


@router.get("/review/{review_id}", response_model=ReviewResponse)
async def get_review_by_id(
    review_id: str,
    session: AsyncSession = Depends(get_session),
) -> ReviewResponse:
    """Retrieve a specific review by ID."""
    record = await get_review(session, review_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Review not found.")

    result = json.loads(record.result_json)
    return ReviewResponse(**result)
