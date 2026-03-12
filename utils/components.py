"""
Cricklytics — Reusable HTML components for Streamlit rendering.
"""

import html as html_lib


def tile(label: str, value: object, delta: str | None = None, delta_dir: str = "up") -> str:
    """Return an HTML KPI tile."""
    safe_label = html_lib.escape(str(label))
    safe_value = html_lib.escape(str(value))
    delta_html = ""
    if delta:
        safe_delta = html_lib.escape(str(delta))
        arrow = "▲ " if delta_dir == "up" else "▼ "
        delta_html = f'<div class="delta {delta_dir}">{arrow}{safe_delta}</div>'
    return (
        f'<div class="tile">'
        f'<div class="label">{safe_label}</div>'
        f'<div class="value">{safe_value}</div>'
        f'{delta_html}'
        f'</div>'
    )


def tile_grid(tiles: list[str]) -> str:
    """Wrap multiple tiles in a responsive grid."""
    inner = "".join(tiles)
    return f'<div class="tile-grid">{inner}</div>'


def stat_row(label: str, value: object) -> str:
    """Render a label–value stat row."""
    safe_label = html_lib.escape(str(label))
    safe_value = html_lib.escape(str(value))
    return f'<div class="stat-row"><span class="sl">{safe_label}</span><span class="sv">{safe_value}</span></div>'


def form_badge(form: str) -> str:
    """Render a colour-coded form badge with text indicator."""
    safe_form = html_lib.escape(str(form))
    # Only allow known class suffixes to prevent injection via CSS class
    allowed = {"good", "average", "poor"}
    suffix = form.lower() if form.lower() in allowed else "poor"
    cls = f"badge-{suffix}"
    indicator = {"good": "●", "average": "◐", "poor": "○"}.get(suffix, "○")
    return f'<span class="{cls}" aria-label="Form: {safe_form}">{indicator} {safe_form}</span>'


def empty_state(icon: str, title: str, description: str) -> str:
    """Render a styled empty-state placeholder card."""
    safe_title = html_lib.escape(str(title))
    safe_desc = html_lib.escape(str(description))
    safe_icon = html_lib.escape(str(icon))
    return (
        f'<div class="empty-state">'
        f'<div class="empty-state-icon" role="img" aria-label="{safe_title}">{safe_icon}</div>'
        f'<div class="empty-state-title">{safe_title}</div>'
        f'<div class="empty-state-desc">{safe_desc}</div>'
        f'</div>'
    )
