"""
Cricklytics — ML model training and prediction utilities.
"""

import logging
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

from config.constants import ML_CV_FOLDS, ML_FEATURES, ML_MAX_ITER, ML_RANDOM_STATE, ML_TEST_SIZE

logger = logging.getLogger(__name__)


class MLResult:
    """Container for ML model results."""

    def __init__(
        self,
        model: LogisticRegression,
        label_encoder: LabelEncoder,
        scaler: StandardScaler,
        accuracy: float,
        cv_accuracy_mean: float,
        cv_accuracy_std: float,
        precision: float,
        recall: float,
        f1: float,
        y_test: np.ndarray,
        y_pred: np.ndarray,
        class_report: str,
    ):
        self.model = model
        self.label_encoder = label_encoder
        self.scaler = scaler
        self.accuracy = accuracy
        self.cv_accuracy_mean = cv_accuracy_mean
        self.cv_accuracy_std = cv_accuracy_std
        self.precision = precision
        self.recall = recall
        self.f1 = f1
        self.y_test = y_test
        self.y_pred = y_pred
        self.class_report = class_report


def train_ml_model(df: pd.DataFrame) -> tuple[pd.DataFrame, MLResult]:
    """Train Logistic Regression with cross-validation and full metrics.

    Returns the DataFrame augmented with predictions and an MLResult container.
    """
    X = df[ML_FEATURES].copy()
    y = df["Form_Label"].copy()

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    # Train / test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=ML_TEST_SIZE, random_state=ML_RANDOM_STATE, stratify=y_encoded
    )

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train model
    model = LogisticRegression(max_iter=ML_MAX_ITER, random_state=ML_RANDOM_STATE)
    model.fit(X_train_scaled, y_train)

    # Test-set predictions
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)

    # Cross-validation on full data
    X_all_scaled = scaler.transform(X)
    cv_scores = cross_val_score(model, X_all_scaled, y_encoded, cv=ML_CV_FOLDS, scoring="accuracy")

    # Classification metrics (weighted for class imbalance)
    precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
    class_report = classification_report(y_test, y_pred, target_names=le.classes_, zero_division=0)

    logger.info(
        "ML model trained — Accuracy: %.2f | CV Mean: %.2f ± %.2f | F1: %.2f",
        accuracy, cv_scores.mean(), cv_scores.std(), f1
    )

    # Predict for all players + confidence
    predictions = model.predict(X_all_scaled)
    probabilities = model.predict_proba(X_all_scaled)
    df["ML_Predicted_Form"] = le.inverse_transform(predictions)
    df["ML_Confidence"] = probabilities.max(axis=1)

    result = MLResult(
        model=model,
        label_encoder=le,
        scaler=scaler,
        accuracy=accuracy,
        cv_accuracy_mean=cv_scores.mean(),
        cv_accuracy_std=cv_scores.std(),
        precision=precision,
        recall=recall,
        f1=f1,
        y_test=y_test,
        y_pred=y_pred,
        class_report=class_report,
    )

    return df, result
