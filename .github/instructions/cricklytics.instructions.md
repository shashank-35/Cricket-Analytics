---
description: "Use when working on the Cricklytics project — covers architecture, coding standards, security rules, ML best practices, and UI conventions for this Streamlit cricket analytics dashboard."
applyTo: "**"
---

# Cricklytics — Project Instructions

## Architecture Rules

- **app.py** is the main Streamlit dashboard entry point — keep UI rendering here
- **api_handler.py** handles all external API communication
- **fetch_players_data.py** is the data collection script (run standalone)
- Extract reusable logic into `utils/` when functions exceed single use
- Keep data processing separate from UI rendering where possible

## Coding Standards

- Use type hints on all function signatures
- Use `logging` module instead of `print()` for all output
- No magic numbers — define constants at module level with descriptive names
- Use `@st.cache_data` for data loading and `@st.cache_resource` for ML models
- Sanitize any user-facing HTML content — avoid raw string interpolation in `unsafe_allow_html`

## Security Rules (CRITICAL)

- **NEVER** commit `.env` or API keys to version control
- Always use `.env.example` with placeholders for documentation
- Pass API keys in HTTP headers, not URL query parameters
- Validate all external API responses before processing
- Sanitize user inputs before embedding in HTML

## ML Conventions

- Use cross-validation instead of single train/test splits
- Include precision, recall, and F1-score alongside accuracy
- Cache trained models with `@st.cache_resource` to avoid retraining on every page load
- Document feature selection rationale
- Handle class imbalance explicitly

## UI/Theme Conventions

- Dark theme colors: use the defined constants (ACCENT, ACCENT2, WARN, DANGER, etc.)
- All Plotly charts must have a descriptive `title` parameter
- Apply `apply_plotly_theme(fig)` to every Plotly figure before rendering
- Use `tile()` and `tile_grid()` helpers for KPI cards
- Chart titles should be human-readable (e.g., "Top 15 — Runs Scored", not "Runs")

## Data Conventions

- CSV is the fallback data source; API is primary when available
- Always call `drop_duplicates(subset='Player')` after loading
- Fill missing values with 0 via `fillna(0)` on load
- Cricket format (T20/ODI/Test) should be documented and consistent
