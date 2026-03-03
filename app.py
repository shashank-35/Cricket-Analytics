"""
Cricklytics Pro — Sports Analytics SaaS Dashboard
Professional-grade cricket analytics with ML-powered predictions
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
from streamlit_option_menu import option_menu
import requests
import os
from dotenv import load_dotenv
from api_handler import get_live_cricket_data

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Cricklytics Pro",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# PROFESSIONAL DARK SaaS THEME
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

PLOTLY_TEMPLATE = dict(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT, family="Inter, sans-serif"),
        title_font=dict(size=16, color=TEXT),
        xaxis=dict(gridcolor=SURFACE, zerolinecolor=SURFACE),
        yaxis=dict(gridcolor=SURFACE, zerolinecolor=SURFACE),
        colorway=[ACCENT, ACCENT2, WARN, DANGER, "#8B5CF6", "#EC4899"],
        margin=dict(l=40, r=20, t=50, b=40),
    )
)

st.markdown("""
<style>
/* ─── Global resets ────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1280px;
}

/* ─── Sidebar (sticky) ─────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #0F172A;
    border-right: 1px solid #1E293B;
    position: sticky;
    top: 0;
    height: 100vh;
}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
    color: #F1F5F9 !important;
}
section[data-testid="stSidebar"] hr {
    border-color: #334155;
}

/* ─── Page header ──────────────────────────────────────── */
.pro-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: .25rem;
}
.pro-header h1 {
    font-size: 1.75rem;
    font-weight: 700;
    color: #F1F5F9;
    margin: 0;
    letter-spacing: -0.5px;
}
.pro-header .badge {
    background: #3B82F6;
    color: #fff;
    font-size: .65rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 999px;
    text-transform: uppercase;
    letter-spacing: .5px;
}
.pro-subtitle {
    color: #94A3B8;
    font-size: .95rem;
    margin-bottom: 1.5rem;
}

/* ─── KPI / Summary Tiles ──────────────────────────────── */
.tile-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 14px;
    margin-bottom: 1.5rem;
}
.tile {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 20px 22px;
    transition: border-color .2s ease;
}
.tile:hover { border-color: #3B82F6; }
.tile .label {
    font-size: .75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: .6px;
    color: #94A3B8;
    margin-bottom: 6px;
}
.tile .value {
    font-size: 1.65rem;
    font-weight: 700;
    color: #F1F5F9;
    line-height: 1.2;
}
.tile .delta {
    font-size: .78rem;
    margin-top: 4px;
}
.delta.up   { color: #10B981; }
.delta.down { color: #EF4444; }

/* ─── Card (generic container) ─────────────────────────── */
.card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
}
.card h3 {
    font-size: 1rem;
    font-weight: 600;
    color: #F1F5F9;
    margin: 0 0 14px 0;
}

/* ─── Form badges ──────────────────────────────────────── */
.badge-good {
    background: rgba(16,185,129,.15);
    color: #10B981;
    padding: 4px 14px;
    border-radius: 999px;
    font-size: .8rem;
    font-weight: 600;
}
.badge-average {
    background: rgba(245,158,11,.15);
    color: #F59E0B;
    padding: 4px 14px;
    border-radius: 999px;
    font-size: .8rem;
    font-weight: 600;
}
.badge-poor {
    background: rgba(239,68,68,.15);
    color: #EF4444;
    padding: 4px 14px;
    border-radius: 999px;
    font-size: .8rem;
    font-weight: 600;
}

/* ─── Stat row (label + value) ─────────────────────────── */
.stat-row {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #334155;
    font-size: .88rem;
}
.stat-row:last-child { border-bottom: none; }
.stat-row .sl { color: #94A3B8; }
.stat-row .sv { color: #F1F5F9; font-weight: 600; }

/* ─── Buttons ──────────────────────────────────────────── */
.stButton>button {
    background: #3B82F6;
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 10px 22px;
    font-weight: 600;
    font-size: .85rem;
    transition: background .2s;
}
.stButton>button:hover { background: #2563EB; }

/* ─── Tabs ─────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid #334155;
}
.stTabs [data-baseweb="tab"] {
    font-weight: 500;
    font-size: .85rem;
    color: #94A3B8;
    border-bottom: 2px solid transparent;
    padding: 8px 20px;
}
.stTabs [aria-selected="true"] {
    color: #3B82F6 !important;
    border-bottom: 2px solid #3B82F6 !important;
    background: transparent !important;
}

/* ─── Dataframes ───────────────────────────────────────── */
.stDataFrame {
    border-radius: 8px;
    overflow: hidden;
}

/* ─── Separator ────────────────────────────────────────── */
.sep { height: 1px; background: #334155; margin: 1.5rem 0; }

/* ─── Section title ────────────────────────────────────── */
.section-title {
    font-size: 1.15rem;
    font-weight: 600;
    color: #F1F5F9;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Hide default Streamlit header bar decorations */
header[data-testid="stHeader"] { background: transparent; }

/* ─── Expander (insights panels) ───────────────────────── */
.streamlit-expanderHeader {
    font-weight: 600 !important;
    color: #F1F5F9 !important;
    background: #1E293B !important;
    border-radius: 8px !important;
}
details[data-testid="stExpander"] {
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    background: #1E293B !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

# ============================================================================
# HELPER: reusable HTML components
# ============================================================================

def tile(label: str, value, delta: str = None, delta_dir: str = "up"):
    """Return an HTML KPI tile."""
    delta_html = ""
    if delta:
        delta_html = f'<div class="delta {delta_dir}">{delta}</div>'
    return (
        f'<div class="tile">'
        f'<div class="label">{label}</div>'
        f'<div class="value">{value}</div>'
        f'{delta_html}'
        f'</div>'
    )

def tile_grid(tiles: list[str]):
    """Wrap multiple tiles in a responsive grid."""
    inner = "".join(tiles)
    return f'<div class="tile-grid">{inner}</div>'

def stat_row(label: str, value):
    return f'<div class="stat-row"><span class="sl">{label}</span><span class="sv">{value}</span></div>'

def form_badge(form: str):
    cls = f"badge-{form.lower()}"
    return f'<span class="{cls}">{form}</span>'

def apply_plotly_theme(fig):
    """Apply consistent SaaS theme to any Plotly figure."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F1F5F9", family="Inter, sans-serif", size=12),
        title_font=dict(size=15, color="#F1F5F9"),
        xaxis=dict(gridcolor="#334155", zerolinecolor="#334155"),
        yaxis=dict(gridcolor="#334155", zerolinecolor="#334155"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94A3B8")),
        margin=dict(l=40, r=20, t=50, b=40),
    )
    return fig

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data
def load_data(filepath: str):
    """Load cricket data from CSV file"""
    try:
        df = pd.read_csv(filepath)
        # Handle missing values
        df = df.fillna(0)
        return df
    except FileNotFoundError:
        st.error(f"❌ File not found: {filepath}")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        st.stop()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_live_data(api_key: str):
    """Load cricket data from live API"""
    df, status, last_updated = get_live_cricket_data(api_key)
    return df, status, last_updated

def load_data_with_source(use_api: bool, api_key: str = None):
    """Load data from API or CSV based on user selection"""
    if use_api and api_key:
        df, status, last_updated = load_live_data(api_key)
        if df is not None:
            return df, status, last_updated
        else:
            st.warning("⚠️ API failed, falling back to CSV data")
            return load_data('cricket_players.csv'), "🟡 Using CSV (API Failed)", ""
    else:
        return load_data('cricket_players.csv'), "📁 Using CSV Data", ""

def calculate_impact_score(df):
    """Calculate Impact Score for each player"""
    df['Impact_Score'] = (df['Batting_Avg'] * df['Strike_Rate']) / 100
    return df

def classify_form(df):
    """Classify player form based on batting average"""
    def get_form(avg):
        if avg >= 45:
            return 'Good'
        elif avg >= 30:
            return 'Average'
        else:
            return 'Poor'
    
    df['Form_Label'] = df['Batting_Avg'].apply(get_form)
    return df

def get_form_color(form):
    """Return color based on form"""
    colors = {
        'Good': '#10b981',
        'Average': '#f59e0b',
        'Poor': '#ef4444'
    }
    return colors.get(form, '#6b7280')

def train_ml_model(df):
    """Train Logistic Regression model to predict player form"""
    # Prepare features and target
    features = ['Batting_Avg', 'Strike_Rate', 'Runs', 'Matches']
    X = df[features]
    y = df['Form_Label']
    
    # Encode labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Predictions
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Predict for all players
    X_all_scaled = scaler.transform(X)
    predictions = model.predict(X_all_scaled)
    df['ML_Predicted_Form'] = le.inverse_transform(predictions)
    
    return df, accuracy, model, le, scaler, y_test, y_pred

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    load_dotenv()

    # ── Page header ──────────────────────────────────────────────────────
    st.markdown(
        '<div class="pro-header">'
        '<h1>Cricklytics Pro</h1>'
        '<span class="badge">v2.0</span>'
        '</div>'
        '<div class="pro-subtitle">Sports-grade cricket analytics &amp; ML predictions</div>',
        unsafe_allow_html=True
    )

    # ── Sticky sidebar ──────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:10px;padding:8px 0 4px;">'
            '<span style="font-size:1.6rem;">🏏</span>'
            '<span style="font-weight:700;font-size:1.1rem;color:#F1F5F9;letter-spacing:-.3px;">Cricklytics Pro</span>'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown("---")

        # Data source selector
        st.markdown('<span style="font-size:.75rem;text-transform:uppercase;letter-spacing:.5px;color:#94A3B8;font-weight:600;">Data Source</span>', unsafe_allow_html=True)
        api_key = os.getenv('CRICKETDATA_API_KEY')
        if api_key:
            use_live_api = st.toggle("Live API", value=True, help="Switch between live API and local CSV")
        else:
            use_live_api = False
            st.caption("No API key — using CSV data")

        st.markdown("---")

        selected = option_menu(
            menu_title=None,
            options=["Dashboard", "Player Analysis", "Player Comparison", "Team Statistics", "ML Prediction", "Settings"],
            icons=["grid-1x2-fill", "person-badge-fill", "people-fill", "bar-chart-line-fill", "cpu-fill", "sliders"],
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#3B82F6", "font-size": "17px"},
                "nav-link": {
                    "font-size": "14px",
                    "font-weight": "500",
                    "text-align": "left",
                    "margin": "2px 0",
                    "border-radius": "8px",
                    "padding": "10px 14px",
                    "--hover-color": "#1E293B",
                    "color": "#94A3B8",
                },
                "nav-link-selected": {
                    "background-color": "rgba(59,130,246,.12)",
                    "color": "#3B82F6",
                    "font-weight": "600",
                },
            }
        )

        st.markdown("---")
        st.markdown(f'<div style="font-size:.7rem;color:#475569;">v2.0 · Professional Analytics</div>', unsafe_allow_html=True)

    # ── Load data ────────────────────────────────────────────────────────
    df, data_status, last_updated = load_data_with_source(use_live_api, api_key)

    # Status bar
    status_cols = st.columns([4, 1])
    with status_cols[1]:
        dot = "🟢" if "API" in data_status and "Failed" not in data_status else "🔵"
        st.caption(f"{dot}  {data_status}")

    # Ensure 'Country' column exists (API data may lack it)
    if 'Country' not in df.columns:
        df['Country'] = 'Unknown'

    # Drop duplicate players (keep first occurrence)
    df = df.drop_duplicates(subset='Player', keep='first').reset_index(drop=True)

    # Feature engineering
    df = calculate_impact_score(df)
    df = classify_form(df)
    df, ml_accuracy, model, le, scaler, y_test, y_pred = train_ml_model(df)

    # ====================================================================
    #  DASHBOARD
    # ====================================================================
    if selected == "Dashboard":
        # ── Summary tiles ────────────────────────────────────────────
        avg_bat = df['Batting_Avg'].mean()
        avg_sr  = df['Strike_Rate'].mean()
        st.markdown(tile_grid([
            tile("Total Players", len(df)),
            tile("Avg Batting Avg", f"{avg_bat:.1f}"),
            tile("Total Runs", f"{df['Runs'].sum():,}"),
            tile("Total Wickets", f"{df['Wickets'].sum():,}"),
            tile("Avg Strike Rate", f"{avg_sr:.1f}"),
            tile("ML Accuracy", f"{ml_accuracy*100:.1f}%"),
        ]), unsafe_allow_html=True)

        # ── Tabbed charts ────────────────────────────────────────────
        tab_overview, tab_scatter, tab_leaders = st.tabs(["Performance Overview", "Scatter Analysis", "Leaderboard"])

        with tab_overview:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="card"><h3>Top 15 — Runs Scored</h3></div>', unsafe_allow_html=True)
                top15 = df.sort_values('Runs', ascending=False).head(15)
                fig = px.bar(
                    top15, x='Player', y='Runs', color='Form_Label',
                    color_discrete_map={'Good': ACCENT2, 'Average': WARN, 'Poor': DANGER},
                )
                fig.update_layout(xaxis_tickangle=-45, height=420, showlegend=True,
                                  legend_title_text="Form")
                st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

            with col2:
                st.markdown('<div class="card"><h3>Wickets — Top Bowlers</h3></div>', unsafe_allow_html=True)
                top_w = df.sort_values('Wickets', ascending=False).head(15)
                fig = px.bar(top_w, x='Player', y='Wickets',
                             color_discrete_sequence=[ACCENT])
                fig.update_layout(xaxis_tickangle=-45, height=420)
                st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

        with tab_scatter:
            # Advanced filter
            with st.container():
                fc1, fc2, fc3 = st.columns(3)
                with fc1:
                    min_matches = st.slider("Min Matches", 0, int(df['Matches'].max()), 0)
                with fc2:
                    form_filter = st.multiselect("Form", ['Good', 'Average', 'Poor'], default=['Good', 'Average', 'Poor'])
                with fc3:
                    country_filter = st.multiselect("Country", sorted(df['Country'].unique()), default=sorted(df['Country'].unique()))

            filtered = df[(df['Matches'] >= min_matches) &
                          (df['Form_Label'].isin(form_filter)) &
                          (df['Country'].isin(country_filter))]

            fig = px.scatter(
                filtered, x='Batting_Avg', y='Strike_Rate',
                color='Form_Label', size='Runs',
                hover_data=['Player', 'Matches', 'Wickets'],
                color_discrete_map={'Good': ACCENT2, 'Average': WARN, 'Poor': DANGER},
            )
            fig.update_layout(height=500)
            st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

            # Expandable insight
            with st.expander("💡 Insight — Batting Average vs Strike Rate"):
                avg_ba = filtered['Batting_Avg'].mean()
                avg_sr = filtered['Strike_Rate'].mean()
                st.markdown(f"**Filtered dataset:** {len(filtered)} players | **Avg Batting Avg:** {avg_ba:.1f} | **Avg SR:** {avg_sr:.1f}")
                st.markdown("Players in the upper-right quadrant combine high consistency (batting average) with aggressive scoring (strike rate) — the most impactful profiles for limited-overs cricket.")

        with tab_leaders:
            st.markdown('<div class="card"><h3>Top Performers</h3></div>', unsafe_allow_html=True)
            leaders = df.nlargest(20, 'Impact_Score')[
                ['Player', 'Country', 'Matches', 'Runs', 'Batting_Avg', 'Strike_Rate', 'Wickets', 'Impact_Score', 'Form_Label']
            ].reset_index(drop=True)
            leaders.index = leaders.index + 1
            st.dataframe(leaders, use_container_width=True, height=600)

    # ====================================================================
    #  PLAYER ANALYSIS
    # ====================================================================
    elif selected == "Player Analysis":
        st.markdown('<div class="section-title">Player Analysis</div>', unsafe_allow_html=True)

        # Filters row
        fc1, fc2 = st.columns([2, 1])
        with fc1:
            player_name = st.selectbox("Select Player", df['Player'].sort_values(), label_visibility="collapsed",
                                       index=0)
        with fc2:
            pass  # placeholder for future filter

        if player_name:
            p = df[df['Player'] == player_name].iloc[0]

            tab_profile, tab_radar, tab_rank = st.tabs(["Profile", "Radar Chart", "Ranking"])

            with tab_profile:
                col1, col2 = st.columns([1, 2])
                with col1:
                    runs_str = f"{int(p['Runs']):,}"
                    bavg_str = f"{p['Batting_Avg']:.2f}"
                    sr_str = f"{p['Strike_Rate']:.2f}"
                    eco_str = f"{p['Economy']:.2f}"
                    imp_str = f"{p['Impact_Score']:.2f}"
                    card_html = (
                        '<div class="card">'
                        + f'<h3>{player_name}</h3>'
                        + f'<div style="margin-bottom:8px;">{form_badge(p["Form_Label"])}</div>'
                        + stat_row("Country", p["Country"])
                        + stat_row("Matches", int(p["Matches"]))
                        + stat_row("Runs", runs_str)
                        + stat_row("Batting Avg", bavg_str)
                        + stat_row("Strike Rate", sr_str)
                        + stat_row("Wickets", int(p["Wickets"]))
                        + stat_row("Economy", eco_str)
                        + stat_row("Impact Score", imp_str)
                        + '</div>'
                    )
                    st.markdown(card_html, unsafe_allow_html=True)

                with col2:
                    # Performance summary tiles
                    rank_runs = int((df['Runs'] > p['Runs']).sum() + 1)
                    rank_avg  = int((df['Batting_Avg'] > p['Batting_Avg']).sum() + 1)
                    rank_imp  = int((df['Impact_Score'] > p['Impact_Score']).sum() + 1)
                    st.markdown(tile_grid([
                        tile("Runs Rank", f"#{rank_runs}", f"of {len(df)}"),
                        tile("Batting Avg Rank", f"#{rank_avg}", f"of {len(df)}"),
                        tile("Impact Rank", f"#{rank_imp}", f"of {len(df)}"),
                    ]), unsafe_allow_html=True)

                    with st.expander("💡 Player Insight", expanded=True):
                        form = p['Form_Label']
                        if form == 'Good':
                            st.success(f"{player_name} is in **excellent form** — batting average of {p['Batting_Avg']:.1f} with a strike rate of {p['Strike_Rate']:.1f}. A reliable first-choice pick.")
                        elif form == 'Average':
                            st.warning(f"{player_name} shows **moderate form**. A batting average of {p['Batting_Avg']:.1f} suggests room for improvement in consistency.")
                        else:
                            st.error(f"{player_name} is in a **lean patch** with a batting average of {p['Batting_Avg']:.1f}. Consider resting or providing targeted coaching.")

            with tab_radar:
                categories = ['Batting Avg', 'Strike Rate', 'Impact Score', 'Matches', 'Wickets']
                values = [
                    p['Batting_Avg'] / df['Batting_Avg'].max() * 100,
                    p['Strike_Rate'] / df['Strike_Rate'].max() * 100,
                    p['Impact_Score'] / df['Impact_Score'].max() * 100,
                    p['Matches'] / df['Matches'].max() * 100,
                    p['Wickets'] / df['Wickets'].max() * 100,
                ]
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=values + [values[0]], theta=categories + [categories[0]],
                    fill='toself', fillcolor="rgba(59,130,246,.15)",
                    line=dict(color=ACCENT, width=2),
                    name=player_name,
                ))
                fig.update_layout(
                    polar=dict(
                        bgcolor="rgba(0,0,0,0)",
                        radialaxis=dict(visible=True, range=[0, 100], gridcolor=SURFACE, color=MUTED),
                        angularaxis=dict(gridcolor=SURFACE, color=MUTED),
                    ),
                    height=480, showlegend=False
                )
                st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

            with tab_rank:
                st.markdown('<div class="card"><h3>Where does this player rank?</h3></div>', unsafe_allow_html=True)
                rank_df = df[['Player', 'Runs', 'Batting_Avg', 'Strike_Rate', 'Wickets', 'Impact_Score']].copy()
                for c in ['Runs', 'Batting_Avg', 'Strike_Rate', 'Wickets', 'Impact_Score']:
                    rank_df[f'{c}_Rank'] = rank_df[c].rank(ascending=False).astype(int)
                row = rank_df[rank_df['Player'] == player_name].iloc[0]
                st.markdown(tile_grid([
                    tile("Runs", f"#{int(row['Runs_Rank'])}"),
                    tile("Batting Avg", f"#{int(row['Batting_Avg_Rank'])}"),
                    tile("Strike Rate", f"#{int(row['Strike_Rate_Rank'])}"),
                    tile("Wickets", f"#{int(row['Wickets_Rank'])}"),
                    tile("Impact Score", f"#{int(row['Impact_Score_Rank'])}"),
                ]), unsafe_allow_html=True)

    # ====================================================================
    #  PLAYER COMPARISON
    # ====================================================================
    elif selected == "Player Comparison":
        st.markdown('<div class="section-title">Player Comparison</div>', unsafe_allow_html=True)

        selected_players = st.multiselect(
            "Select 2-4 Players", df['Player'].sort_values(), max_selections=4
        )

        if len(selected_players) >= 2:
            cdf = df[df['Player'].isin(selected_players)]

            tab_table, tab_charts = st.tabs(["Comparison Table", "Visual Comparison"])

            with tab_table:
                display_cols = ['Player', 'Country', 'Matches', 'Runs', 'Batting_Avg', 'Strike_Rate', 'Wickets', 'Economy', 'Impact_Score', 'Form_Label']
                st.dataframe(cdf[display_cols].set_index('Player'), use_container_width=True)

            with tab_charts:
                metric_choice = st.selectbox("Metric", ['Runs', 'Batting_Avg', 'Strike_Rate', 'Wickets', 'Economy', 'Impact_Score'])
                fig = px.bar(
                    cdf, x='Player', y=metric_choice, color='Player',
                    color_discrete_sequence=[ACCENT, ACCENT2, WARN, DANGER],
                )
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

                # Overlay radar
                with st.expander("📊 Radar Overlay"):
                    cats = ['Batting Avg', 'Strike Rate', 'Impact Score', 'Matches', 'Wickets']
                    fig = go.Figure()
                    colors = [ACCENT, ACCENT2, WARN, DANGER]
                    for idx, (_, row) in enumerate(cdf.iterrows()):
                        vals = [
                            row['Batting_Avg'] / df['Batting_Avg'].max() * 100,
                            row['Strike_Rate'] / df['Strike_Rate'].max() * 100,
                            row['Impact_Score'] / df['Impact_Score'].max() * 100,
                            row['Matches'] / df['Matches'].max() * 100,
                            row['Wickets'] / df['Wickets'].max() * 100,
                        ]
                        fig.add_trace(go.Scatterpolar(
                            r=vals + [vals[0]], theta=cats + [cats[0]],
                            fill='toself', name=row['Player'],
                            fillcolor=f"rgba({','.join(str(int(colors[idx][i:i+2], 16)) for i in (1,3,5))},.08)",
                            line=dict(color=colors[idx], width=2),
                        ))
                    fig.update_layout(
                        polar=dict(
                            bgcolor="rgba(0,0,0,0)",
                            radialaxis=dict(visible=True, range=[0, 100], gridcolor=SURFACE, color=MUTED),
                            angularaxis=dict(gridcolor=SURFACE, color=MUTED),
                        ),
                        height=480
                    )
                    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

        elif len(selected_players) == 1:
            st.info("Select at least **2 players** to compare.")
        else:
            st.info("Choose 2-4 players from the dropdown to begin.")

    # ====================================================================
    #  TEAM STATISTICS
    # ====================================================================
    elif selected == "Team Statistics":
        st.markdown('<div class="section-title">Team Statistics</div>', unsafe_allow_html=True)

        # Summary tiles
        st.markdown(tile_grid([
            tile("Avg Matches", f"{df['Matches'].mean():.0f}"),
            tile("Avg Runs", f"{df['Runs'].mean():.0f}"),
            tile("Avg Batting Avg", f"{df['Batting_Avg'].mean():.1f}"),
            tile("Avg Strike Rate", f"{df['Strike_Rate'].mean():.1f}"),
            tile("Avg Wickets", f"{df['Wickets'].mean():.0f}"),
            tile("Avg Economy", f"{df['Economy'].mean():.1f}"),
        ]), unsafe_allow_html=True)

        tab_dist, tab_corr, tab_form = st.tabs(["Distributions", "Correlations", "Form Analysis"])

        with tab_dist:
            metric = st.selectbox("Distribution of", ['Batting_Avg', 'Strike_Rate', 'Runs', 'Wickets', 'Economy'], key='dist_metric')
            fig = px.histogram(df, x=metric, nbins=20, color_discrete_sequence=[ACCENT],
                               marginal="box")
            fig.update_layout(height=420)
            st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

            with st.expander("💡 Distribution Insight"):
                m = df[metric]
                st.markdown(f"**Mean:** {m.mean():.2f} | **Median:** {m.median():.2f} | **Std Dev:** {m.std():.2f} | **Skewness:** {m.skew():.2f}")

        with tab_corr:
            corr_cols = ['Runs', 'Batting_Avg', 'Strike_Rate', 'Wickets', 'Economy', 'Impact_Score']
            corr_matrix = df[corr_cols].corr()
            fig = px.imshow(
                corr_matrix, text_auto=".2f",
                color_continuous_scale=["#EF4444", "#1E293B", "#3B82F6"],
                aspect="auto"
            )
            fig.update_layout(height=500)
            st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

        with tab_form:
            col1, col2 = st.columns(2)
            with col1:
                form_counts = df['Form_Label'].value_counts()
                fig = px.pie(
                    values=form_counts.values, names=form_counts.index,
                    color=form_counts.index,
                    color_discrete_map={'Good': ACCENT2, 'Average': WARN, 'Poor': DANGER},
                    hole=.45,
                )
                fig.update_layout(height=380)
                st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

            with col2:
                country_form = df.groupby(['Country', 'Form_Label']).size().reset_index(name='Count')
                fig = px.bar(country_form, x='Country', y='Count', color='Form_Label',
                             barmode='stack',
                             color_discrete_map={'Good': ACCENT2, 'Average': WARN, 'Poor': DANGER})
                fig.update_layout(height=380, xaxis_tickangle=-45)
                st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

            with st.expander("💡 Form Breakdown by Country"):
                pivot = df.pivot_table(index='Country', columns='Form_Label', values='Player', aggfunc='count', fill_value=0)
                st.dataframe(pivot, use_container_width=True)

    # ====================================================================
    #  ML PREDICTION
    # ====================================================================
    elif selected == "ML Prediction":
        st.markdown('<div class="section-title">ML-Powered Form Prediction</div>', unsafe_allow_html=True)

        # Model performance tiles
        match_rate = ((df['Form_Label'] == df['ML_Predicted_Form']).sum() / len(df)) * 100
        st.markdown(tile_grid([
            tile("Algorithm", "Logistic Reg."),
            tile("Accuracy", f"{ml_accuracy*100:.1f}%"),
            tile("Match Rate", f"{match_rate:.1f}%"),
            tile("Features", "4"),
        ]), unsafe_allow_html=True)

        tab_pred, tab_cm, tab_feat = st.tabs(["Predictions", "Confusion Matrix", "Feature Importance"])

        with tab_pred:
            pred_df = df[['Player', 'Batting_Avg', 'Strike_Rate', 'Runs', 'Matches',
                          'Form_Label', 'ML_Predicted_Form']].copy()
            pred_df['Match'] = pred_df['Form_Label'] == pred_df['ML_Predicted_Form']
            pred_df['Match'] = pred_df['Match'].map({True: '✅', False: '❌'})
            pred_df.columns = ['Player', 'Bat Avg', 'SR', 'Runs', 'Matches', 'Rule-Based', 'ML Predicted', 'Match']
            st.dataframe(pred_df, use_container_width=True, height=500)

        with tab_cm:
            cm = confusion_matrix(y_test, y_pred)
            labels = le.inverse_transform(np.unique(y_test))
            fig = px.imshow(cm, text_auto=True, x=labels, y=labels,
                            color_continuous_scale=["#0F172A", "#3B82F6"],
                            labels=dict(x="Predicted", y="Actual"))
            fig.update_layout(height=440)
            st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

        with tab_feat:
            feature_names = ['Batting_Avg', 'Strike_Rate', 'Runs', 'Matches']
            for idx, class_name in enumerate(le.classes_):
                with st.expander(f"Coefficients — {class_name} class", expanded=(idx == 0)):
                    coefficients = model.coef_[idx]
                    fig = px.bar(
                        x=feature_names, y=coefficients,
                        color=coefficients,
                        color_continuous_scale=["#EF4444", "#334155", "#10B981"],
                        labels={'x': 'Feature', 'y': 'Coefficient'},
                    )
                    fig.update_layout(height=320, showlegend=False)
                    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

    # ====================================================================
    #  SETTINGS
    # ====================================================================
    elif selected == "Settings":
        st.markdown('<div class="section-title">Settings & Info</div>', unsafe_allow_html=True)

        tab_about, tab_data = st.tabs(["About", "Dataset"])

        with tab_about:
            st.markdown(
                '<div class="card">'
                '<h3>About Cricklytics Pro</h3>'
                '<p style="color:#94A3B8;line-height:1.7;font-size:.9rem;">'
                'Cricklytics Pro is a professional-grade cricket analytics dashboard combining real-time data, '
                'advanced visualisations and machine-learning predictions. Built for analysts, coaches and fans '
                'who demand actionable insights.'
                '</p>'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown(tile_grid([
                tile("Frontend", "Streamlit"),
                tile("ML Engine", "Scikit-learn"),
                tile("Viz", "Plotly"),
                tile("Data", "Pandas & NumPy"),
            ]), unsafe_allow_html=True)

            with st.expander("🗺 Roadmap"):
                st.markdown(
                    "- Advanced ML models (Random Forest, XGBoost)\n"
                    "- Player career trajectory prediction\n"
                    "- Match outcome prediction\n"
                    "- Real-time match analytics\n"
                    "- PDF report exports\n"
                    "- User authentication & personal dashboards"
                )

        with tab_data:
            st.markdown('<div class="card"><h3>Dataset Preview</h3></div>', unsafe_allow_html=True)
            st.dataframe(df.head(15), use_container_width=True)
            csv = df.to_csv(index=False)
            st.download_button(
                "Download Full Dataset", csv,
                file_name="cricklytics_export.csv", mime="text/csv"
            )

# ============================================================================
# RUN APPLICATION
# ============================================================================
if __name__ == "__main__":
    main()
