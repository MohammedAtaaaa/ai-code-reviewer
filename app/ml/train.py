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


def generate_synthetic_samples(
    n_per_class: int = 300,
) -> tuple[list[dict[str, float]], list[int]]:
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
        textwrap.dedent("""\
        from dataclasses import dataclass


        @dataclass
        class Point:
            \"\"\"Represents a 2D point.\"\"\"
            x: float
            y: float

            def distance_to(self, other: 'Point') -> float:
                \"\"\"Calculate Euclidean distance to another point.\"\"\"
                return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

            def midpoint(self, other: 'Point') -> 'Point':
                \"\"\"Return the midpoint between two points.\"\"\"
                return Point((self.x + other.x) / 2, (self.y + other.y) / 2)
        """),
        textwrap.dedent("""\
        from typing import Iterator


        def fibonacci(n: int) -> Iterator[int]:
            \"\"\"Generate the first n Fibonacci numbers.\"\"\"
            a, b = 0, 1
            for _ in range(n):
                yield a
                a, b = b, a + b


        def is_prime(n: int) -> bool:
            \"\"\"Check if a number is prime.\"\"\"
            if n < 2:
                return False
            for i in range(2, int(n ** 0.5) + 1):
                if n % i == 0:
                    return False
            return True
        """),
        textwrap.dedent("""\
        import json
        from pathlib import Path


        def load_config(path: str) -> dict:
            \"\"\"Load configuration from a JSON file.\"\"\"
            config_path = Path(path)
            if not config_path.exists():
                raise FileNotFoundError(f"Config not found: {path}")
            with config_path.open() as f:
                return json.load(f)


        def save_config(path: str, data: dict) -> None:
            \"\"\"Save configuration to a JSON file.\"\"\"
            with Path(path).open("w") as f:
                json.dump(data, f, indent=2)
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
        textwrap.dedent("""\
        def fetch_data(url, timeout=30, retry=3, headers=None):
            import requests
            for i in range(retry):
                try:
                    resp = requests.get(url, timeout=timeout, headers=headers)
                    if resp.status_code == 200:
                        return resp.json()
                except Exception:
                    if i == retry - 1:
                        raise
            return None
        """),
        textwrap.dedent("""\
        def validate(data):
            errors = []
            if not data.get('name'):
                errors.append('name required')
            if not data.get('email'):
                errors.append('email required')
            if data.get('age') and data['age'] < 0:
                errors.append('invalid age')
            if data.get('age') and data['age'] > 150:
                errors.append('invalid age')
            if len(errors) > 0:
                return False, errors
            return True, []
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
        textwrap.dedent("""\
        import hashlib
        def check_pass(p):
            h = hashlib.md5(p.encode()).hexdigest()
            db_pass = "5f4dcc3b5aa765d61d8327deb882cf99"
            if h == db_pass:
                return True
            return False
        """),
        textwrap.dedent("""\
        def query_db(table, user_input):
            import sqlite3
            conn = sqlite3.connect("app.db")
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table} WHERE name = '{user_input}'")
            return cursor.fetchall()
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
    samples, labels = generate_synthetic_samples(n_per_class=400)

    names = feature_names()
    feature_matrix = np.array([[s.get(n, 0) for n in names] for s in samples])
    target = np.array(labels)

    scaler = StandardScaler()
    scaled = scaler.fit_transform(feature_matrix)

    model = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        random_state=42,
        min_samples_split=5,
        min_samples_leaf=3,
        subsample=0.9,
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
