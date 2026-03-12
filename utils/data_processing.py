"""
Cricklytics — Data processing and validation utilities.
"""

import logging
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from config.constants import (
    REQUIRED_COLUMNS,
    FORM_GOOD_THRESHOLD,
    FORM_AVG_THRESHOLD,
)

logger = logging.getLogger(__name__)


def validate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and clean a cricket players DataFrame.

    - Ensures required columns exist (fills missing ones with defaults).
    - Fills NaN with 0.
    - Drops duplicate players.
    - Clamps numeric values to sensible ranges.
    """
    # Fill missing required columns
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            default = "Unknown" if col in ("Player", "Country") else 0
            df[col] = default
            logger.warning("Column '%s' missing — filled with '%s'", col, default)

    df = df.fillna(0)
    df = df.drop_duplicates(subset="Player", keep="first").reset_index(drop=True)

    # Clamp unrealistic numeric ranges
    numeric_clamps: dict[str, tuple[float, float]] = {
        "Batting_Avg": (0, 100),
        "Strike_Rate": (0, 400),
        "Economy": (0, 20),
        "Matches": (0, 600),
    }
    for col, (lo, hi) in numeric_clamps.items():
        if col in df.columns:
            df[col] = df[col].clip(lower=lo, upper=hi)

    return df


def calculate_impact_score(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate Impact Score = (Batting_Avg * Strike_Rate) / 100."""
    df["Impact_Score"] = (df["Batting_Avg"] * df["Strike_Rate"]) / 100
    return df


def classify_form(df: pd.DataFrame) -> pd.DataFrame:
    """Classify player form based on batting average thresholds."""
    def _label(avg: float) -> str:
        if avg >= FORM_GOOD_THRESHOLD:
            return "Good"
        elif avg >= FORM_AVG_THRESHOLD:
            return "Average"
        return "Poor"

    df["Form_Label"] = df["Batting_Avg"].apply(_label)
    return df


def get_form_color(form: str) -> str:
    """Return hex color for a form label."""
    from config.constants import FORM_COLOR_MAP
    return FORM_COLOR_MAP.get(form, "#6b7280")


def find_similar_players(df: pd.DataFrame, player_name: str, n: int = 5) -> pd.DataFrame:
    """Return the top N players closest to *player_name* in feature space.

    Uses Euclidean distance after standard scaling of batting/bowling features.
    """
    features = ["Batting_Avg", "Strike_Rate", "Runs", "Matches", "Wickets"]
    df_feat = df[features].fillna(0)

    scaler = StandardScaler()
    scaled = scaler.fit_transform(df_feat.values)

    player_mask = df["Player"] == player_name
    if not player_mask.any():
        return pd.DataFrame()

    player_pos = df.index.get_loc(df.index[player_mask][0])
    player_vec = scaled[player_pos]

    distances = np.sqrt(((scaled - player_vec) ** 2).sum(axis=1))
    df_result = df.copy()
    df_result["_dist"] = distances
    similar = df_result[df_result["Player"] != player_name].nsmallest(n, "_dist")
    return similar.drop("_dist", axis=1).reset_index(drop=True)


def compute_team_strength(df: pd.DataFrame, player_names: list) -> dict:
    """Compute composite batting + bowling strength for a list of player names.

    Returns a dict with keys:
        ``batting_strength``, ``bowling_strength``, ``overall_strength``
    """
    team = df[df["Player"].isin(player_names)].copy()
    if team.empty:
        return {"batting_strength": 0.0, "bowling_strength": 0.0, "overall_strength": 0.0}

    # Top-6 Impact Scores drive batting strength
    top_batters = team.nlargest(min(6, len(team)), "Impact_Score")
    batting_strength = float(top_batters["Impact_Score"].sum())

    # Top-4 bowlers (wickets > 0), ranked by wickets / economy
    bowlers = team[team["Wickets"] > 0].copy()
    if not bowlers.empty:
        bowlers["_bowl_score"] = bowlers["Wickets"] / bowlers["Economy"].clip(lower=0.01)
        bowling_strength = float(
            bowlers.nlargest(min(4, len(bowlers)), "_bowl_score")["_bowl_score"].sum()
        )
    else:
        bowling_strength = 0.0

    return {
        "batting_strength": batting_strength,
        "bowling_strength": bowling_strength,
        "overall_strength": batting_strength + bowling_strength,
    }
