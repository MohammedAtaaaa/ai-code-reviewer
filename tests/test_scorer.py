"""Tests for the multi-dimensional scoring system."""

from app.services.analyzer import CodeAnalyzer
from app.services.scorer import CodeScorer


class TestCodeScorer:
    def setup_method(self) -> None:
        self.scorer = CodeScorer()
        self.analyzer = CodeAnalyzer()

    def test_clean_code_high_score(self) -> None:
        code = 'def greet(name: str) -> str:\n    """Greet."""\n    return f"Hi, {name}"\n'
        analysis = self.analyzer.analyze(code)
        breakdown, suggestions = self.scorer.score(analysis, ml_score=8.5, ml_label="good")
        assert breakdown.overall >= 7.0
        assert breakdown.security == 10.0

    def test_bad_code_low_security_score(self) -> None:
        code = 'def f(x):\n    eval(x)\n    password = "secret"\n    return x\n'
        analysis = self.analyzer.analyze(code)
        breakdown, suggestions = self.scorer.score(analysis, ml_score=3.0, ml_label="bad")
        assert breakdown.security < 7.0
        assert len(suggestions) > 0

    def test_no_ml_score_uses_default(self) -> None:
        code = "x = 1\n"
        analysis = self.analyzer.analyze(code)
        breakdown, _ = self.scorer.score(analysis, ml_score=None)
        assert breakdown.ml_quality == 7.0  # default

    def test_all_scores_in_range(self) -> None:
        code = "x = 1\ny = 2\nprint(x + y)\n"
        analysis = self.analyzer.analyze(code)
        breakdown, _ = self.scorer.score(analysis, ml_score=6.0, ml_label="medium")
        for attr in ("overall", "clean_code", "readability", "maintainability",
                      "security", "ml_quality"):
            val = getattr(breakdown, attr)
            assert 0 <= val <= 10, f"{attr} = {val} is out of range"

    def test_explanations_structure(self) -> None:
        code = "x = 1\n"
        analysis = self.analyzer.analyze(code)
        breakdown, _ = self.scorer.score(analysis)
        assert isinstance(breakdown.explanations, dict)
        for key in ("clean_code", "readability", "maintainability", "security", "ml_quality"):
            assert key in breakdown.explanations
            assert isinstance(breakdown.explanations[key], list)

    def test_summary_generation(self) -> None:
        code = "x = 1\nprint(x)\n"
        analysis = self.analyzer.analyze(code)
        breakdown, suggestions = self.scorer.score(analysis, ml_score=7.0, ml_label="good")
        summary = self.scorer.generate_summary(breakdown, analysis, suggestions)
        assert "Code Quality:" in summary
        assert "Clean Code:" in summary
        assert "Security:" in summary
