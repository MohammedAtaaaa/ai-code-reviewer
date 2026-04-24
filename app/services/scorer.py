"""Combine multiple signals into a detailed code quality score (0–10)."""

import logging
from dataclasses import dataclass, field

from app.config import settings
from app.services.analyzer import AnalysisResult

logger = logging.getLogger(__name__)

SEVERITY_WEIGHTS = {
    "critical": 2.0,
    "error": 1.5,
    "warning": 0.8,
    "info": 0.3,
}


@dataclass
class ScoreBreakdown:
    """Detailed breakdown of the code quality score."""

    overall: float = 10.0
    clean_code: float = 10.0
    readability: float = 10.0
    maintainability: float = 10.0
    security: float = 10.0
    ml_quality: float = 10.0
    explanations: dict[str, list[str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.explanations:
            self.explanations = {
                "clean_code": [],
                "readability": [],
                "maintainability": [],
                "security": [],
                "ml_quality": [],
            }


class CodeScorer:
    """Produces a multi-dimensional score from static analysis, complexity, and ML."""

    def score(
        self,
        analysis: AnalysisResult,
        ml_score: float | None = None,
        ml_label: str | None = None,
        ml_confidence: float | None = None,
        code_length: int = 0,
    ) -> tuple[ScoreBreakdown, list[str]]:
        """
        Returns (breakdown, suggestions).

        Score dimensions (each 0–10):
        - clean_code: unused vars/imports, duplicates, code structure
        - readability: naming conventions, line length, docstrings, comments
        - maintainability: complexity, function size, nesting, modularity
        - security: vulnerability patterns, risky calls, hardcoded secrets
        - ml_quality: ML model prediction (if available)

        Overall = weighted combination of all sub-scores.
        """
        breakdown = ScoreBreakdown()
        suggestions: list[str] = []

        self._score_clean_code(breakdown, analysis, suggestions)
        self._score_readability(breakdown, analysis, suggestions)
        self._score_maintainability(breakdown, analysis, suggestions)
        self._score_security(breakdown, analysis, suggestions)
        self._score_ml_quality(
            breakdown, ml_score, ml_label, ml_confidence, suggestions
        )

        breakdown.overall = self._compute_weighted_overall(breakdown)

        # Clamp all scores
        for attr in (
            "overall", "clean_code", "readability",
            "maintainability", "security", "ml_quality",
        ):
            setattr(breakdown, attr, round(max(0.0, min(10.0, getattr(breakdown, attr))), 1))

        return breakdown, suggestions

    def _score_clean_code(
        self,
        breakdown: ScoreBreakdown,
        analysis: AnalysisResult,
        suggestions: list[str],
    ) -> None:
        score = 10.0

        # Unused variables/imports
        n_unused = len(analysis.unused_items)
        if n_unused > 0:
            penalty = min(n_unused * SEVERITY_WEIGHTS["warning"], 4.0)
            score -= penalty
            names = [item.name for item in analysis.unused_items[:3]]
            extra = n_unused - 3
            suffix = f" and {extra} more" if extra > 0 else ""
            suggestions.append(
                f"Remove unused {analysis.unused_items[0].kind}s: "
                f"{', '.join(names)}{suffix}."
            )
            breakdown.explanations["clean_code"].append(
                f"{n_unused} unused item(s) detected — each wastes reader attention."
            )

        # Duplicate code
        n_dupes = len(analysis.duplicates)
        if n_dupes > 0:
            avg_sim = sum(d.similarity for d in analysis.duplicates) / n_dupes
            penalty = min(n_dupes * avg_sim * SEVERITY_WEIGHTS["warning"], 3.0)
            score -= penalty
            suggestions.append(
                "Extract duplicated logic into shared helper functions "
                "to improve maintainability."
            )
            breakdown.explanations["clean_code"].append(
                f"{n_dupes} duplicate block(s) found with "
                f"avg similarity {avg_sim:.0%}."
            )

        # Function issues (too long, too many args, etc.)
        n_func = len(analysis.function_issues)
        if n_func > 0:
            penalty = min(n_func * SEVERITY_WEIGHTS["warning"], 3.0)
            score -= penalty
            for fi in analysis.function_issues[:2]:
                suggestions.append(fi.message)
            breakdown.explanations["clean_code"].append(
                f"{n_func} function-level issue(s): "
                "consider refactoring large or complex functions."
            )

        breakdown.clean_code = max(0.0, score)

    def _score_readability(
        self,
        breakdown: ScoreBreakdown,
        analysis: AnalysisResult,
        suggestions: list[str],
    ) -> None:
        score = 10.0

        # Naming convention violations
        n_naming = len(analysis.naming_issues)
        if n_naming > 0:
            penalty = min(n_naming * SEVERITY_WEIGHTS["info"], 3.0)
            score -= penalty
            suggestions.append(
                "Follow PEP 8 naming conventions: snake_case for "
                "functions/variables, PascalCase for classes."
            )
            breakdown.explanations["readability"].append(
                f"{n_naming} naming convention violation(s) detected."
            )

        # Comment and docstring ratio from complexity
        if analysis.complexity:
            cr = analysis.complexity.comment_ratio
            if cr < 0.05:
                score -= 1.5
                suggestions.append(
                    "Add comments and docstrings to improve code readability."
                )
                breakdown.explanations["readability"].append(
                    f"Very low comment ratio ({cr:.1%}) — code lacks documentation."
                )
            elif cr < 0.10:
                score -= 0.5
                breakdown.explanations["readability"].append(
                    f"Low comment ratio ({cr:.1%}) — consider adding more docs."
                )

        breakdown.readability = max(0.0, score)

    def _score_maintainability(
        self,
        breakdown: ScoreBreakdown,
        analysis: AnalysisResult,
        suggestions: list[str],
    ) -> None:
        score = 10.0

        if analysis.complexity:
            cc = analysis.complexity.cyclomatic_complexity
            mi = analysis.complexity.maintainability_index

            if cc > 20:
                penalty = min((cc - 20) * 0.15, 3.0)
                score -= penalty
                suggestions.append(
                    f"High cyclomatic complexity ({cc}). "
                    "Break down complex logic into smaller, focused functions."
                )
                breakdown.explanations["maintainability"].append(
                    f"Cyclomatic complexity is {cc} (target: ≤20)."
                )
            elif cc > 10:
                penalty = (cc - 10) * 0.05
                score -= penalty
                breakdown.explanations["maintainability"].append(
                    f"Moderate cyclomatic complexity ({cc})."
                )

            if mi < 40:
                score -= 2.0
                suggestions.append(
                    f"Low maintainability index ({mi:.1f}/100). "
                    "Consider simplifying the code structure and adding documentation."
                )
                breakdown.explanations["maintainability"].append(
                    f"Maintainability index is {mi:.1f}/100 — needs significant work."
                )
            elif mi < 65:
                score -= 1.0
                suggestions.append(
                    f"Moderate maintainability index ({mi:.1f}/100). "
                    "Some areas could benefit from refactoring."
                )
                breakdown.explanations["maintainability"].append(
                    f"Maintainability index is {mi:.1f}/100 — room for improvement."
                )
            else:
                breakdown.explanations["maintainability"].append(
                    f"Maintainability index is {mi:.1f}/100 — good."
                )

            # Function count vs lines ratio
            fc = analysis.complexity.function_count
            sloc = analysis.complexity.sloc
            if sloc > 50 and fc == 0:
                score -= 1.0
                suggestions.append(
                    "Large file with no functions — consider modularizing."
                )

        breakdown.maintainability = max(0.0, score)

    def _score_security(
        self,
        breakdown: ScoreBreakdown,
        analysis: AnalysisResult,
        suggestions: list[str],
    ) -> None:
        score = 10.0

        for sec in analysis.security_issues:
            weight = SEVERITY_WEIGHTS.get(sec.severity, 0.8)
            # Dynamic weight: critical issues penalized more heavily
            if sec.severity == "critical":
                weight *= 1.5
            score -= weight
            breakdown.explanations["security"].append(
                f"[{sec.severity.upper()}] {sec.rule}: {sec.message[:80]}"
            )

        n_sec = len(analysis.security_issues)
        if n_sec > 0:
            critical = sum(1 for s in analysis.security_issues if s.severity == "critical")
            if critical:
                suggestions.append(
                    f"SECURITY: {critical} critical issue(s) — fix before deploying."
                )
            else:
                suggestions.append(
                    f"{n_sec} security concern(s) detected — review and address."
                )
        else:
            breakdown.explanations["security"].append("No security issues detected.")

        breakdown.security = max(0.0, score)

    def _score_ml_quality(
        self,
        breakdown: ScoreBreakdown,
        ml_score: float | None,
        ml_label: str | None,
        ml_confidence: float | None,
        suggestions: list[str],
    ) -> None:
        if ml_score is not None:
            breakdown.ml_quality = ml_score
            conf_str = f"{ml_confidence:.0%}" if ml_confidence else "N/A"
            breakdown.explanations["ml_quality"].append(
                f"ML prediction: {ml_label} (confidence: {conf_str})."
            )
            if ml_confidence and ml_confidence < settings.ml_confidence_threshold:
                breakdown.explanations["ml_quality"].append(
                    f"Low ML confidence ({conf_str}) — prediction may be unreliable."
                )
        else:
            breakdown.ml_quality = 7.0  # neutral default
            breakdown.explanations["ml_quality"].append(
                "ML prediction unavailable for this language."
            )

    def _compute_weighted_overall(self, breakdown: ScoreBreakdown) -> float:
        return (
            breakdown.clean_code * settings.weight_clean_code
            + breakdown.readability * settings.weight_readability
            + breakdown.maintainability * settings.weight_maintainability
            + breakdown.security * settings.weight_security
            + breakdown.ml_quality * settings.weight_ml_quality
        )

    def generate_summary(
        self,
        breakdown: ScoreBreakdown,
        analysis: AnalysisResult,
        suggestions: list[str],
    ) -> str:
        """Generate a human-readable review summary."""
        score = breakdown.overall
        if score >= 8.5:
            quality = "Excellent"
            emoji_desc = "great"
        elif score >= 7.0:
            quality = "Good"
            emoji_desc = "solid"
        elif score >= 5.0:
            quality = "Needs Improvement"
            emoji_desc = "fair"
        elif score >= 3.0:
            quality = "Poor"
            emoji_desc = "concerning"
        else:
            quality = "Critical"
            emoji_desc = "needs significant rework"

        parts = [
            f"Code Quality: {quality} ({score}/10)",
            f"Overall assessment: This code is {emoji_desc}.",
            "",
            "Score Breakdown:",
            f"  Clean Code:      {breakdown.clean_code}/10",
            f"  Readability:     {breakdown.readability}/10",
            f"  Maintainability: {breakdown.maintainability}/10",
            f"  Security:        {breakdown.security}/10",
            f"  ML Quality:      {breakdown.ml_quality}/10",
        ]

        if analysis.total_issues == 0:
            parts.append("\nNo issues detected — clean code!")
        else:
            parts.append(f"\nFound {analysis.total_issues} issue(s) to address.")

        if analysis.security_issues:
            critical = sum(
                1 for s in analysis.security_issues if s.severity == "critical"
            )
            if critical:
                parts.append(
                    f"SECURITY: {critical} critical security issue(s) found — "
                    "fix these before deploying."
                )

        if suggestions:
            parts.append("\nTop recommendations:")
            for i, s in enumerate(suggestions[:5], 1):
                parts.append(f"  {i}. {s}")

        return "\n".join(parts)
