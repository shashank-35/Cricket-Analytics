"""Tests for utils/data_processing.py"""

import pandas as pd
import pytest
from utils.data_processing import calculate_impact_score, classify_form, validate_dataframe


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Small DataFrame mimicking cricket_players.csv."""
    return pd.DataFrame({
        "Player": ["Alice", "Bob", "Charlie"],
        "Country": ["India", "Australia", "England"],
        "Player_ID": [1, 2, 3],
        "Matches": [100, 50, 10],
        "Runs": [5000, 1200, 300],
        "Batting_Avg": [50.0, 35.0, 15.0],
        "Strike_Rate": [90.0, 120.0, 60.0],
        "Wickets": [5, 80, 150],
        "Economy": [6.0, 5.5, 4.8],
    })


class TestValidateDataframe:
    def test_fills_missing_columns(self) -> None:
        df = pd.DataFrame({"Player": ["X"], "Runs": [10]})
        result = validate_dataframe(df)
        assert "Country" in result.columns
        assert "Wickets" in result.columns

    def test_drops_duplicates(self) -> None:
        df = pd.DataFrame({
            "Player": ["A", "A"],
            "Country": ["IN", "IN"],
            "Matches": [10, 20],
            "Runs": [100, 200],
            "Batting_Avg": [30, 40],
            "Strike_Rate": [80, 90],
            "Wickets": [5, 10],
            "Economy": [6, 7],
        })
        result = validate_dataframe(df)
        assert len(result) == 1

    def test_clamps_extreme_batting_avg(self) -> None:
        df = pd.DataFrame({
            "Player": ["X"],
            "Country": ["IN"],
            "Matches": [10],
            "Runs": [100],
            "Batting_Avg": [150.0],  # unrealistic
            "Strike_Rate": [80.0],
            "Wickets": [5],
            "Economy": [6.0],
        })
        result = validate_dataframe(df)
        assert result["Batting_Avg"].iloc[0] == 100.0

    def test_fills_nan(self) -> None:
        df = pd.DataFrame({
            "Player": ["X"],
            "Country": [None],
            "Matches": [None],
            "Runs": [None],
            "Batting_Avg": [None],
            "Strike_Rate": [None],
            "Wickets": [None],
            "Economy": [None],
        })
        result = validate_dataframe(df)
        assert result["Runs"].iloc[0] == 0


class TestCalculateImpactScore:
    def test_formula(self, sample_df: pd.DataFrame) -> None:
        result = calculate_impact_score(sample_df)
        expected = (50.0 * 90.0) / 100
        assert result["Impact_Score"].iloc[0] == pytest.approx(expected)

    def test_column_added(self, sample_df: pd.DataFrame) -> None:
        result = calculate_impact_score(sample_df)
        assert "Impact_Score" in result.columns


class TestClassifyForm:
    def test_good_form(self, sample_df: pd.DataFrame) -> None:
        result = classify_form(sample_df)
        assert result.loc[result["Player"] == "Alice", "Form_Label"].iloc[0] == "Good"

    def test_average_form(self, sample_df: pd.DataFrame) -> None:
        result = classify_form(sample_df)
        assert result.loc[result["Player"] == "Bob", "Form_Label"].iloc[0] == "Average"

    def test_poor_form(self, sample_df: pd.DataFrame) -> None:
        result = classify_form(sample_df)
        assert result.loc[result["Player"] == "Charlie", "Form_Label"].iloc[0] == "Poor"
