"""Tests for utils/ml_model.py"""

import pandas as pd
import pytest
from utils.data_processing import classify_form
from utils.ml_model import train_ml_model, MLResult


@pytest.fixture
def ml_df() -> pd.DataFrame:
    """DataFrame large enough for train/test split."""
    import random
    random.seed(42)
    rows = []
    for i in range(60):
        ba = random.uniform(10, 70)
        sr = random.uniform(50, 180)
        runs = random.randint(100, 15000)
        matches = random.randint(10, 300)
        rows.append({
            "Player": f"Player_{i}",
            "Batting_Avg": round(ba, 1),
            "Strike_Rate": round(sr, 1),
            "Runs": runs,
            "Matches": matches,
        })
    df = pd.DataFrame(rows)
    df = classify_form(df)
    return df


class TestTrainMlModel:
    def test_returns_dataframe_and_result(self, ml_df: pd.DataFrame) -> None:
        df, result = train_ml_model(ml_df)
        assert isinstance(df, pd.DataFrame)
        assert isinstance(result, MLResult)

    def test_predictions_column_added(self, ml_df: pd.DataFrame) -> None:
        df, _ = train_ml_model(ml_df)
        assert "ML_Predicted_Form" in df.columns
        assert "ML_Confidence" in df.columns

    def test_confidence_range(self, ml_df: pd.DataFrame) -> None:
        df, _ = train_ml_model(ml_df)
        assert df["ML_Confidence"].between(0, 1).all()

    def test_accuracy_is_reasonable(self, ml_df: pd.DataFrame) -> None:
        _, result = train_ml_model(ml_df)
        # Accuracy should be above random chance (>33% for 3 classes)
        assert result.accuracy > 0.33

    def test_cv_scores_populated(self, ml_df: pd.DataFrame) -> None:
        _, result = train_ml_model(ml_df)
        assert result.cv_accuracy_mean > 0
        assert result.cv_accuracy_std >= 0

    def test_class_report_present(self, ml_df: pd.DataFrame) -> None:
        _, result = train_ml_model(ml_df)
        assert "precision" in result.class_report.lower()
        assert "recall" in result.class_report.lower()
        assert "f1-score" in result.class_report.lower()
