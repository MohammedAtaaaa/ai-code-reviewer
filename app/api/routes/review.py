"""Code review endpoint."""

import contextlib
import json
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.review import (
    BatchReviewRequest,
    BatchReviewResponse,
    BatchReviewSummary,
    CodeIssue,
    MLPrediction,
    ReviewRequest,
    ReviewResponse,
    ScoreBreakdownResponse,
    SecurityFlag,
    Severity,
)
from app.auth.dependencies import get_current_user
from app.cache import code_hash, get_cached_review, set_cached_review
from app.config import settings
from app.db.crud import create_review, get_next_version, get_review
from app.db.database import get_session
from app.db.models import User
from app.ml.predict import get_predictor
from app.services.analyzer import CodeAnalyzer
from app.services.scorer import CodeScorer

logger = logging.getLogger(__name__)

router = APIRouter()
analyzer = CodeAnalyzer()
scorer = CodeScorer()


async def _perform_review(
    code: str,
    language: str,
    session: AsyncSession,
    user: User | None = None,
    skip_cache: bool = False,
) -> ReviewResponse:
    """Core review logic shared by single and batch endpoints."""
    if not code.strip():
        raise HTTPException(status_code=400, detail="Code must not be empty.")

    # Check cache
    cache_key = code_hash(code, language)
    if not skip_cache:
        cached = get_cached_review(cache_key)
        if cached:
            logger.info("Cache hit for %s", cache_key[:12])
            return ReviewResponse(**cached, cached=True)

    # Run static analysis
    analysis = analyzer.analyze(code, language)

    # Run ML prediction
    ml_result = None
    ml_score = None
    ml_label = None
    ml_confidence = None
    if language == "python":
        try:
            predictor = get_predictor()
            ml_result = predictor.predict(code)
            ml_score = ml_result["score"]
            ml_label = ml_result["quality_label"]
            ml_confidence = ml_result["confidence"]
        except Exception:
            logger.warning("ML prediction failed — degrading gracefully")

    # Compute scores
    code_lines = len(code.splitlines())
    breakdown, suggestions = scorer.score(
        analysis,
        ml_score=ml_score,
        ml_label=ml_label,
        ml_confidence=ml_confidence,
        code_length=code_lines,
    )

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
                suggestion=f"Rename '{ni.name}' to follow "
                f"{ni.expected_convention} convention.",
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
            probabilities=ml_result.get("probabilities", {}),
            meets_threshold=(
                ml_result["confidence"] >= settings.ml_confidence_threshold
            ),
        )

    # Score breakdown
    score_breakdown = ScoreBreakdownResponse(
        overall=breakdown.overall,
        clean_code=breakdown.clean_code,
        readability=breakdown.readability,
        maintainability=breakdown.maintainability,
        security=breakdown.security,
        ml_quality=breakdown.ml_quality,
        explanations=breakdown.explanations,
    )

    # Generate summary
    summary = scorer.generate_summary(breakdown, analysis, suggestions)

    review_id = str(uuid.uuid4())

    # Determine version
    version = await get_next_version(session, cache_key)

    response = ReviewResponse(
        id=review_id,
        issues=issues,
        suggestions=suggestions,
        score=breakdown.overall,
        score_breakdown=score_breakdown,
        security_flags=security_flags,
        ml_prediction=ml_prediction,
        complexity_metrics=complexity_metrics,
        summary=summary,
        version=version,
    )

    # Persist to database
    with contextlib.suppress(Exception):
        await create_review(
            session=session,
            review_id=review_id,
            code=code,
            code_hash=cache_key,
            language=language,
            score=breakdown.overall,
            clean_code_score=breakdown.clean_code,
            readability_score=breakdown.readability,
            maintainability_score=breakdown.maintainability,
            security_score=breakdown.security,
            ml_quality_score=breakdown.ml_quality,
            issue_count=len(issues),
            security_flag_count=len(security_flags),
            ml_quality_label=ml_result["quality_label"] if ml_result else None,
            ml_confidence=ml_result["confidence"] if ml_result else None,
            result_json=response.model_dump(mode="json"),
            user_id=user.id if user else None,
            version=version,
        )

    # Cache the result
    with contextlib.suppress(Exception):
        set_cached_review(cache_key, response.model_dump(mode="json"))

    return response


@router.post("/review", response_model=ReviewResponse)
async def review_code(
    request: ReviewRequest,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user),
) -> ReviewResponse:
    """
    Analyze submitted code and return a comprehensive review.

    The review includes:
    - Detected issues (bugs, bad practices, anti-patterns)
    - Improvement suggestions from a senior reviewer perspective
    - A code quality score (0–10) with detailed breakdown
    - Security warnings for risky patterns
    - ML-based quality prediction with confidence level
    """
    logger.info(
        "Review request: language=%s, length=%d, user=%s",
        request.language,
        len(request.code),
        user.username if user else "anonymous",
    )
    return await _perform_review(
        code=request.code,
        language=request.language,
        session=session,
        user=user,
    )


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


@router.post("/review-batch", response_model=BatchReviewResponse)
async def batch_review(
    request: BatchReviewRequest,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user),
) -> BatchReviewResponse:
    """
    Review multiple code snippets in a single request.

    Maximum batch size is controlled by the MAX_BATCH_SIZE setting.
    """
    if len(request.items) > settings.max_batch_size:
        raise HTTPException(
            status_code=400,
            detail=f"Batch size exceeds maximum ({settings.max_batch_size}).",
        )

    logger.info(
        "Batch review: %d items, user=%s",
        len(request.items),
        user.username if user else "anonymous",
    )

    reviews: list[ReviewResponse] = []
    for item in request.items:
        review = await _perform_review(
            code=item.code,
            language=item.language,
            session=session,
            user=user,
        )
        reviews.append(review)

    scores = [r.score for r in reviews]
    summary = BatchReviewSummary(
        total_files=len(reviews),
        average_score=round(sum(scores) / len(scores), 1),
        min_score=min(scores),
        max_score=max(scores),
        total_issues=sum(len(r.issues) for r in reviews),
        total_security_flags=sum(len(r.security_flags) for r in reviews),
    )

    return BatchReviewResponse(reviews=reviews, summary=summary)
