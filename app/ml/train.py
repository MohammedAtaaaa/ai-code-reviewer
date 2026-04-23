"""Train a code quality classification model using synthetic data."""

import json
import os
import random
import textwrap
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler

from app.ml.features import extract_features, feature_names

LABELS = {"good": 0, "medium": 1, "bad": 2}
LABEL_NAMES = {v: k for k, v in LABELS.items()}

MODEL_DIR = Path(__file__).parent / "model"


def generate_synthetic_samples(n_per_class: int = 200) -> tuple[list[dict[str, float]], list[int]]:
    """Generate synthetic code samples with known quality labels."""
    samples: list[dict[str, float]] = []
    labels: list[int] = []

    good_templates = [
        textwrap.dedent("""\
        def calculate_total(items: list[float], tax_rate: float = 0.1) -> float:
            \"\"\"Calculate total price including tax.\"\"\"
            subtotal = sum(items)
            tax = subtotal * tax_rate
            return round(subtotal + tax, 2)
        """),
        textwrap.dedent("""\
        class UserService:
            \"\"\"Handles user-related operations.\"\"\"

            def __init__(self, repository):
                self.repository = repository

            def get_user(self, user_id: int):
                \"\"\"Retrieve a user by ID.\"\"\"
                return self.repository.find_by_id(user_id)

            def create_user(self, name: str, email: str):
                \"\"\"Create a new user.\"\"\"
                user = {"name": name, "email": email}
                return self.repository.save(user)
        """),
        textwrap.dedent("""\
        import logging

        logger = logging.getLogger(__name__)


        def process_batch(items: list[dict], batch_size: int = 100) -> list[dict]:
            \"\"\"Process items in batches.\"\"\"
            results = []
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                processed = [transform(item) for item in batch]
                results.extend(processed)
                logger.info("Processed batch %d", i // batch_size + 1)
            return results


        def transform(item: dict) -> dict:
            \"\"\"Transform a single item.\"\"\"
            return {k: str(v).strip() for k, v in item.items()}
        """),
    ]

    medium_templates = [
        textwrap.dedent("""\
        def process(data, flag, mode, extra=None):
            result = []
            for item in data:
                if flag:
                    if mode == 'a':
                        result.append(item * 2)
                    elif mode == 'b':
                        result.append(item + 1)
                    else:
                        result.append(item)
                else:
                    result.append(item)
            return result
        """),
        textwrap.dedent("""\
        class handler:
            def Handle(self, req):
                d = req.get('data')
                if d:
                    r = []
                    for x in d:
                        r.append(x)
                    return r
                return []
        """),
        textwrap.dedent("""\
        def calc(a, b, c, d, e, f):
            temp = a + b
            temp2 = c * d
            if temp > temp2:
                return temp - e + f
            else:
                return temp2 - e + f
        """),
    ]

    bad_templates = [
        textwrap.dedent("""\
        def f(x):
            eval(x)
            password = "admin123"
            import os
            os.system("rm -rf /")
            y = 1
            z = 2
            return x
        """),
        textwrap.dedent("""\
        def do_everything(a,b,c,d,e,f,g,h):
            if a:
                if b:
                    if c:
                        if d:
                            if e:
                                if f:
                                    return g+h
            result = a+b+c+d+e+f+g+h
            data = a+b+c+d+e+f+g+h
            return result
        """),
        textwrap.dedent("""\
        import pickle
        def LoadData(Path):
            F = open(Path)
            D = F.read()
            F.close()
            Result = pickle.loads(D)
            token = "sk_live_abc123def456"
            return Result
        """),
    ]

    rng = random.Random(42)

    for _ in range(n_per_class):
        code = rng.choice(good_templates)
        feats = extract_features(code)
        feats = _add_noise(feats, rng, scale=0.05)
        samples.append(feats)
        labels.append(LABELS["good"])

    for _ in range(n_per_class):
        code = rng.choice(medium_templates)
        feats = extract_features(code)
        feats = _add_noise(feats, rng, scale=0.1)
        samples.append(feats)
        labels.append(LABELS["medium"])

    for _ in range(n_per_class):
        code = rng.choice(bad_templates)
        feats = extract_features(code)
        feats = _add_noise(feats, rng, scale=0.1)
        samples.append(feats)
        labels.append(LABELS["bad"])

    return samples, labels


def _add_noise(
    features: dict[str, float], rng: random.Random, scale: float = 0.1
) -> dict[str, float]:
    noisy = {}
    for key, val in features.items():
        noise = rng.gauss(0, max(abs(val) * scale, 0.1))
        noisy[key] = max(0, val + noise)
    return noisy


def train_model(
    save_path: str | None = None,
) -> tuple[GradientBoostingClassifier, StandardScaler, dict]:
    """Train the code quality classifier and save artifacts."""
    samples, labels = generate_synthetic_samples(n_per_class=300)

    names = feature_names()
    feature_matrix = np.array([[s.get(n, 0) for n in names] for s in samples])
    target = np.array(labels)

    scaler = StandardScaler()
    scaled = scaler.fit_transform(feature_matrix)

    model = GradientBoostingClassifier(
        n_estimators=150,
        max_depth=5,
        learning_rate=0.1,
        random_state=42,
        min_samples_split=5,
        min_samples_leaf=3,
    )

    scores = cross_val_score(model, scaled, target, cv=5, scoring="accuracy")
    model.fit(scaled, target)

    metrics = {
        "cv_accuracy_mean": float(np.mean(scores)),
        "cv_accuracy_std": float(np.std(scores)),
        "n_samples": len(target),
        "feature_names": names,
        "labels": LABEL_NAMES,
    }

    if save_path is None:
        save_path = str(MODEL_DIR)

    os.makedirs(save_path, exist_ok=True)
    joblib.dump(model, os.path.join(save_path, "code_quality_model.joblib"))
    joblib.dump(scaler, os.path.join(save_path, "scaler.joblib"))
    with open(os.path.join(save_path, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    return model, scaler, metrics


if __name__ == "__main__":
    _model, _scaler, _metrics = train_model()
    print("Model trained successfully!")
    print(f"CV Accuracy: {_metrics['cv_accuracy_mean']:.3f} ± {_metrics['cv_accuracy_std']:.3f}")
