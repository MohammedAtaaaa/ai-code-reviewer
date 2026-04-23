"""Combine multiple signals into a final code quality score (0–10)."""

from app.services.analyzer import AnalysisResult

SEVERITY_WEIGHTS = {
    "critical": 1.5,
    "error": 1.0,
    "warning": 0.5,
    "info": 0.2,
}


class CodeScorer:
    """Produces a final score combining static analysis, complexity, and ML signals."""

    def score(
        self,
        analysis: AnalysisResult,
        ml_score: float | None = None,
        code_length: int = 0,
    ) -> tuple[float, list[str]]:
        """
        Returns (score, suggestions) where score is 0.0–10.0.

        Scoring breakdown:
        - Start at 10.0
        - Deduct for issues based on severity
        - Deduct for high complexity
        - Blend with ML prediction if available
        """
        score = 10.0
        suggestions: list[str] = []

        # --- Issue deductions ---
        issue_penalty = 0.0

        issue_penalty += len(analysis.unused_items) * SEVERITY_WEIGHTS["warning"]
        issue_penalty += len(analysis.naming_issues) * SEVERITY_WEIGHTS["info"]
        issue_penalty += len(analysis.function_issues) * SEVERITY_WEIGHTS["warning"]

        for dup in analysis.duplicates:
            issue_penalty += SEVERITY_WEIGHTS["warning"] * dup.similarity

        for sec in analysis.security_issues:
            issue_penalty += SEVERITY_WEIGHTS.get(sec.severity, 0.5)

        lines = max(code_length, 1)
        normalized_penalty = min(issue_penalty * (50 / max(lines, 50)), 5.0)
        score -= normalized_penalty

        # --- Complexity deductions ---
        if analysis.complexity:
            cc = analysis.complexity.cyclomatic_complexity
            mi = analysis.complexity.maintainability_index

            if cc > 20:
                complexity_penalty = min((cc - 20) * 0.1, 2.0)
                score -= complexity_penalty
                suggestions.append(
                    f"High cyclomatic complexity ({cc}). "
                    "Break down complex logic into smaller, focused functions."
                )

            if mi < 40:
                score -= 1.0
                suggestions.append(
                    f"Low maintainability index ({mi:.1f}/100). "
                    "Consider simplifying the code structure and adding documentation."
                )
            elif mi < 65:
                score -= 0.5
                suggestions.append(
                    f"Moderate maintainability index ({mi:.1f}/100). "
                    "Some areas could benefit from refactoring."
                )

        # --- Generate suggestions based on issues ---
        if analysis.unused_items:
            names = [item.name for item in analysis.unused_items[:3]]
            extra = len(analysis.unused_items) - 3
            suffix = f" and {extra} more" if extra > 0 else ""
            suggestions.append(
                f"Remove unused {analysis.unused_items[0].kind}s: {', '.join(names)}{suffix}."
            )

        if analysis.naming_issues:
            suggestions.append(
                "Follow PEP 8 naming conventions: snake_case for functions/variables, "
                "PascalCase for classes."
            )

        if analysis.function_issues:
            for fi in analysis.function_issues[:2]:
                suggestions.append(fi.message)

        if analysis.duplicates:
            suggestions.append(
                "Extract duplicated logic into shared helper functions to improve maintainability."
            )

        # --- Blend with ML score ---
        if ml_score is not None:
            score = score * 0.7 + ml_score * 0.3

        score = max(0.0, min(10.0, score))
        return round(score, 1), suggestions

    def generate_summary(
        self, score: float, analysis: AnalysisResult, suggestions: list[str]
    ) -> str:
        """Generate a human-readable review summary."""
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
        ]

        if analysis.total_issues == 0:
            parts.append("No issues detected — clean code!")
        else:
            parts.append(f"Found {analysis.total_issues} issue(s) to address.")

        if analysis.security_issues:
            critical = sum(1 for s in analysis.security_issues if s.severity == "critical")
            if critical:
                parts.append(
                    f"SECURITY: {critical} critical security issue(s) found — "
                    "fix these before deploying."
                )

        if analysis.complexity and analysis.complexity.cyclomatic_complexity > 15:
            parts.append(
                "COMPLEXITY: The code has high cyclomatic complexity. "
                "Consider refactoring for better readability."
            )

        if suggestions:
            parts.append("\nTop recommendations:")
            for i, sug in enumerate(suggestions[:5], 1):
                parts.append(f"  {i}. {sug}")

        return "\n".join(parts)
