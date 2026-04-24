"""ML prediction service for code quality classification."""

import logging
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler

from app.config import settings
from app.ml.features import extract_features, feature_names
from app.ml.train import LABEL_NAMES, train_model

logger = logging.getLogger(__name__)

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
            logger.info("No saved model found — training new model...")
            self._model, self._scaler, _ = train_model(str(MODEL_DIR))
        else:
            self._model = joblib.load(model_path)
            self._scaler = joblib.load(scaler_path)
            logger.info("ML model loaded from %s", model_path)

        self._loaded = True

    def predict(self, source: str) -> dict:
        """
        Predict code quality.

        Returns:
            {
                "quality_label": "good" | "medium" | "bad",
                "confidence": float (0.0-1.0),
                "probabilities": {"good": float, "medium": float, "bad": float},
                "meets_threshold": bool,
                "score": float (0-10 scale mapped from prediction)
            }
        """
        if not self._loaded:
            self.load()

        if self._model is None or self._scaler is None:
            raise RuntimeError("ML model not loaded")

        features = extract_features(source)
        names = feature_names()
        feature_matrix = np.array([[features.get(n, 0) for n in names]])
        scaled = self._scaler.transform(feature_matrix)

        prediction = self._model.predict(scaled)[0]
        probabilities = self._model.predict_proba(scaled)[0]

        label = LABEL_NAMES[prediction]
        confidence = float(np.max(probabilities))
        meets_threshold = confidence >= settings.ml_confidence_threshold

        prob_dict = {LABEL_NAMES[i]: float(p) for i, p in enumerate(probabilities)}

        score_map = {"good": 8.5, "medium": 5.5, "bad": 2.5}
        weighted_score = sum(
            score_map[LABEL_NAMES[i]] * p for i, p in enumerate(probabilities)
        )

        logger.debug(
            "ML prediction: %s (conf=%.3f, threshold_met=%s)",
            label, confidence, meets_threshold,
        )

        return {
            "quality_label": label,
            "confidence": round(confidence, 3),
            "probabilities": {k: round(v, 3) for k, v in prob_dict.items()},
            "meets_threshold": meets_threshold,
            "score": round(weighted_score, 1),
        }


_predictor = CodeQualityPredictor()


def get_predictor() -> CodeQualityPredictor:
    """Get the singleton predictor instance."""
    if not _predictor._loaded:
        _predictor.load()
    return _predictor
