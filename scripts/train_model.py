#!/usr/bin/env python3
"""Standalone script to train the code quality ML model."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ml.train import train_model  # noqa: E402


def main() -> None:
    print("Training code quality classification model...")
    model, scaler, metrics = train_model()
    print(f"Training complete!")
    print(f"  CV Accuracy: {metrics['cv_accuracy_mean']:.3f} ± {metrics['cv_accuracy_std']:.3f}")
    print(f"  Samples: {metrics['n_samples']}")
    print(f"  Features: {len(metrics['feature_names'])}")
    print(f"  Model saved to: app/ml/model/")


if __name__ == "__main__":
    main()
