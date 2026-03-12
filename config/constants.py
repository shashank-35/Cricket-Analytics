"""
Cricklytics — Centralized constants and theme configuration.
"""

# ============================================================================
# UI THEME COLORS
# ============================================================================
ACCENT  = "#3B82F6"   # primary blue
ACCENT2 = "#10B981"   # success green
WARN    = "#F59E0B"   # amber
DANGER  = "#EF4444"   # red
BG_DARK = "#0F172A"   # slate-900
CARD_BG = "#1E293B"   # slate-800
SURFACE = "#334155"   # slate-700
TEXT    = "#F1F5F9"   # slate-100
MUTED   = "#94A3B8"   # slate-400

# Secondary / tertiary text colors
SECONDARY_TEXT = "#64748B"   # slate-500 — labels, country tags
LABEL_COLOR    = "#475569"   # slate-600 — timestamps, muted labels
BTN_HOVER      = "#2563EB"   # blue-600 — button hover

# Chart color scales
COLOR_SCALE_DIVERGING: list[str]   = [DANGER, WARN, ACCENT2]       # red → amber → green
COLOR_SCALE_CORRELATION: list[str] = [DANGER, CARD_BG, ACCENT]     # red → dark → blue
COLOR_SCALE_SEQUENTIAL: list[str]  = [BG_DARK, ACCENT]             # dark → blue

# Chart sizing
CHART_TITLE_SIZE = 15
CHART_AXIS_SIZE  = 12

FORM_COLOR_MAP: dict[str, str] = {
    "Good": ACCENT2,
    "Average": WARN,
    "Poor": DANGER,
}

# ============================================================================
# DATA CONSTANTS
# ============================================================================
CSV_FILE_PATH = "cricket_players.csv"
REQUIRED_COLUMNS = ["Player", "Country", "Matches", "Runs", "Batting_Avg", "Strike_Rate", "Wickets", "Economy"]

# Form classification thresholds (batting average)
FORM_GOOD_THRESHOLD = 45
FORM_AVG_THRESHOLD  = 30

# ============================================================================
# LAYOUT / UI CONSTANTS
# ============================================================================
DEFAULT_LEADERBOARD_SIZE = 20
SIMILAR_PLAYERS_COUNT = 5
DREAM_XI_SIZE = 11
XI_MIN_BATSMEN = 1
XI_MAX_BATSMEN = 7
XI_DEFAULT_BATSMEN = 4
XI_MIN_ALLROUNDERS = 0
XI_MAX_ALLROUNDERS = 5
XI_DEFAULT_ALLROUNDERS = 2
XI_MIN_BOWLERS = 1
XI_MAX_BOWLERS = 7
XI_DEFAULT_BOWLERS = 4
XI_MIN_WICKETKEEPERS = 1
XI_MAX_WICKETKEEPERS = 2
XI_DEFAULT_WICKETKEEPERS = 1
MIN_MATCHES_FILTER = 0
TOP_CONTRIBUTORS_COUNT = 5
MIN_TEAM_SIZE = 6

# ============================================================================
# ML CONSTANTS
# ============================================================================
ML_FEATURES = ["Batting_Avg", "Strike_Rate", "Runs", "Matches"]
ML_TEST_SIZE = 0.2
ML_RANDOM_STATE = 42
ML_MAX_ITER = 1000
ML_CV_FOLDS = 5

# ============================================================================
# API CONSTANTS
# ============================================================================
API_BASE_URL = "https://api.cricapi.com/v1"
API_TIMEOUT_SECONDS = 10
API_RATE_LIMIT_SECONDS = 1
API_CACHE_TTL_SECONDS = 300  # 5 minutes
