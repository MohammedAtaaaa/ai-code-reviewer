"""ML prediction service for code quality classification."""

from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler

from app.ml.features import extract_features, feature_names
from app.ml.train import LABEL_NAMES, train_model

MODEL_DIR = Path(__file__).parent / "model"


class CodeQualityPredictor:
    """Predicts code quality using a trained ML model."""

    def __init__(self) -> None:
        self._model: GradientBoostingClassifier | None = None
        self._scaler: StandardScaler | None = None
        self._loaded = False

    def load(self) -> None:
        model_path = MODEL_DIR / "code_quality_model.joblib"
        scaler_path = MODEL_DIR / "scaler.joblib"

        if not model_path.exists() or not scaler_path.exists():
            self._model, self._scaler, _ = train_model(str(MODEL_DIR))
        else:
            self._model = joblib.load(model_path)
            self._scaler = joblib.load(scaler_path)

        self._loaded = True

    def predict(self, source: str) -> dict:
        """
        Predict code quality.

        Returns:
            {
                "quality_label": "good" | "medium" | "bad",
                "confidence": float (0.0-1.0),
                "probabilities": {"good": float, "medium": float, "bad": float},
                "score": float (0-10 scale mapped from prediction)
            }
        """
        if not self._loaded:
            self.load()

        assert self._model is not None
        assert self._scaler is not None

        features = extract_features(source)
        names = feature_names()
        feature_matrix = np.array([[features.get(n, 0) for n in names]])
        scaled = self._scaler.transform(feature_matrix)

        prediction = self._model.predict(scaled)[0]
        probabilities = self._model.predict_proba(scaled)[0]

        label = LABEL_NAMES[prediction]
        confidence = float(np.max(probabilities))

        prob_dict = {LABEL_NAMES[i]: float(p) for i, p in enumerate(probabilities)}

        score_map = {"good": 8.5, "medium": 5.5, "bad": 2.5}
        weighted_score = sum(
            score_map[LABEL_NAMES[i]] * p for i, p in enumerate(probabilities)
        )

        return {
            "quality_label": label,
            "confidence": round(confidence, 3),
            "probabilities": {k: round(v, 3) for k, v in prob_dict.items()},
            "score": round(weighted_score, 1),
        }


_predictor = CodeQualityPredictor()


def get_predictor() -> CodeQualityPredictor:
    """Get the singleton predictor instance."""
    if not _predictor._loaded:
        _predictor.load()
    return _predictor
