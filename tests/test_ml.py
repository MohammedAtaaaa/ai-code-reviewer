"""Tests for ML feature extraction and prediction."""

import textwrap

from app.ml.features import extract_features, feature_names
from app.ml.predict import CodeQualityPredictor


class TestFeatureExtraction:
    def test_extracts_basic_features(self) -> None:
        code = textwrap.dedent("""\
            def add(a, b):
                return a + b
        """)
        features = extract_features(code)
        assert features["function_count"] == 1
        assert features["loc"] >= 2
        assert features["sloc"] >= 2

    def test_feature_names_match(self) -> None:
        code = "x = 1\n"
        features = extract_features(code)
        names = feature_names()
        for name in names:
            assert name in features, f"Missing feature: {name}"

    def test_handles_syntax_error(self) -> None:
        features = extract_features("def broken(:\n")
        assert features["loc"] == 1
        assert features["function_count"] == 0


class TestPredictor:
    def test_predicts_good_code(self) -> None:
        code = textwrap.dedent("""\
            def calculate_total(items: list[float], tax_rate: float = 0.1) -> float:
                \"\"\"Calculate total price including tax.\"\"\"
                subtotal = sum(items)
                tax = subtotal * tax_rate
                return round(subtotal + tax, 2)
        """)
        predictor = CodeQualityPredictor()
        result = predictor.predict(code)
        assert result["quality_label"] in ("good", "medium", "bad")
        assert 0 <= result["confidence"] <= 1
        assert 0 <= result["score"] <= 10

    def test_predicts_bad_code(self) -> None:
        code = textwrap.dedent("""\
            def f(x):
                eval(x)
                password = "admin123"
                y = 1
                z = 2
                return x
        """)
        predictor = CodeQualityPredictor()
        result = predictor.predict(code)
        assert result["quality_label"] in ("good", "medium", "bad")
        assert result["score"] <= 8  # should not be rated highly

    def test_returns_probabilities(self) -> None:
        code = "x = 1\nprint(x)\n"
        predictor = CodeQualityPredictor()
        result = predictor.predict(code)
        assert "probabilities" in result
        probs = result["probabilities"]
        assert abs(sum(probs.values()) - 1.0) < 0.01
