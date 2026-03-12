"""
Cricklytics Pro — Sports Analytics SaaS Dashboard
Professional-grade cricket analytics with ML-powered predictions
"""

import logging
import os
from datetime import datetime
from html import escape as html_escape
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from sklearn.metrics import confusion_matrix
from streamlit_option_menu import option_menu

from config.constants import (
    ACCENT, ACCENT2, BG_DARK, CARD_BG, COLOR_SCALE_CORRELATION,
    COLOR_SCALE_DIVERGING, COLOR_SCALE_SEQUENTIAL, CSV_FILE_PATH,
    DANGER, DEFAULT_LEADERBOARD_SIZE, DREAM_XI_SIZE, FORM_COLOR_MAP,
    LABEL_COLOR, MIN_MATCHES_FILTER, MIN_TEAM_SIZE, MUTED,
    SECONDARY_TEXT, SIMILAR_PLAYERS_COUNT, SURFACE, TEXT, TOP_CONTRIBUTORS_COUNT,
    WARN, XI_DEFAULT_ALLROUNDERS, XI_DEFAULT_BATSMEN, XI_DEFAULT_BOWLERS,
    XI_DEFAULT_WICKETKEEPERS, XI_MAX_ALLROUNDERS, XI_MAX_BATSMEN,
    XI_MAX_BOWLERS, XI_MAX_WICKETKEEPERS, XI_MIN_ALLROUNDERS,
    XI_MIN_BATSMEN, XI_MIN_BOWLERS, XI_MIN_WICKETKEEPERS,
)
from utils.components import empty_state, form_badge, stat_row, tile, tile_grid
from utils.data_processing import (
    calculate_impact_score, classify_form, compute_team_strength,
    find_similar_players, validate_dataframe,
)
from utils.ml_model import MLResult, train_ml_model

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

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

def _load_css() -> None:
    """Load CSS from external file (cached by Streamlit on first render)."""
    css_path = Path(__file__).parent / "static" / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)
    else:
        logger.warning("CSS file not found: %s", css_path)

_load_css()

# ============================================================================
# HELPER: Plotly theme
# ============================================================================

def apply_plotly_theme(fig: go.Figure) -> go.Figure:
    """Apply consistent SaaS theme to any Plotly figure."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT, family="Inter, sans-serif", size=12),
        title_font=dict(size=15, color=TEXT),
        xaxis=dict(gridcolor=SURFACE, zerolinecolor=SURFACE),
        yaxis=dict(gridcolor=SURFACE, zerolinecolor=SURFACE),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED)),
        margin=dict(l=40, r=20, t=50, b=40),
    )
    return fig

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data
def load_data(filepath: str) -> pd.DataFrame:
    """Load cricket data from CSV file."""
    try:
        df = pd.read_csv(filepath)
        df = validate_dataframe(df)
        return df
    except FileNotFoundError:
        st.error(f"File not found: {filepath}")
        st.stop()
    except Exception as e:
        logger.error("Error loading data: %s", e)
        st.error(f"Error loading data: {e}")
        st.stop()

@st.cache_resource
def get_ml_results(df_hash: str, df_json: str) -> MLResult:
    """Train and cache the ML model (retrains only when data changes)."""
    df = pd.read_json(df_json)
    _, result = train_ml_model(df)
    return result


def refresh_csv_from_api(api_key: str) -> tuple[bool, str]:
    """Re-fetch player list from CricAPI and overwrite the local CSV."""
    try:
        from fetch_players_data import BulkPlayerDataFetcher
        fetcher = BulkPlayerDataFetcher(api_key)
        players_list = fetcher.fetch_all_players(max_players=500)
        if not players_list:
            return False, "No players returned from API"
        df = fetcher.create_comprehensive_dataset(players_list)
        fetcher.save_to_csv(df, CSV_FILE_PATH)
        return True, f"Successfully refreshed {len(df)} players from CricAPI"
    except Exception as e:
        logger.error("API refresh failed: %s", e)
        return False, str(e)


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

    # ── Sidebar ─────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:10px;padding:8px 0 4px;">'
            f'<span style="font-size:1.6rem;" role="img" aria-label="Cricket bat">🏏</span>'
            f'<span style="font-weight:700;font-size:1.1rem;color:{TEXT};letter-spacing:-.3px;">Cricklytics Pro</span>'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown("---")

        search_query: str = st.text_input(
            "🔍 Search player",
            value=st.session_state.get("player_search", ""),
            placeholder="Type player name…",
            key="player_search",
            label_visibility="collapsed",
        )

        st.markdown("---")

        selected = option_menu(
            menu_title=None,
            options=[
                "Dashboard", "Player Analysis", "Career Trajectory",
                "Head-to-Head", "Player Comparison", "Team Statistics",
                "Dream XI Builder", "ML Prediction", "Match Prediction", "Settings",
            ],
            icons=[
                "grid-1x2-fill", "person-badge-fill", "graph-up-arrow",
                "shield-fill-check", "people-fill", "bar-chart-line-fill",
                "star-fill", "cpu-fill", "lightning-fill", "sliders",
            ],
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
            },
        )

        st.markdown("---")

        # Data source info
        csv_path = Path(CSV_FILE_PATH)
        if csv_path.exists():
            last_mod = datetime.fromtimestamp(csv_path.stat().st_mtime).strftime("%d %b %Y, %H:%M")
            st.markdown(
                f'<div style="font-size:.72rem;color:{LABEL_COLOR};line-height:1.8;">'
                f'📁 <b style="color:{SECONDARY_TEXT};">{csv_path.name}</b><br>'
                f'🕒 Updated: {last_mod}'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            f'<div style="font-size:.7rem;color:{LABEL_COLOR};margin-top:8px;">v2.0 · Professional Analytics</div>',
            unsafe_allow_html=True,
        )

    # ── Load data (always CSV) ───────────────────────────────────────────
    with st.spinner("Loading data…"):
        df = load_data(CSV_FILE_PATH)

    if "Country" not in df.columns:
        df["Country"] = "Unknown"

    df = calculate_impact_score(df)
    df = classify_form(df)

    # Search-filtered player options (used by all single-player selectors)
    all_players = sorted(df["Player"].tolist())
    if search_query:
        player_options = [p for p in all_players if search_query.lower() in p.lower()] or all_players
    else:
        player_options = all_players

    # ML model (cached — only retrains when data changes)
    df_hash = str(
        pd.util.hash_pandas_object(df[["Player", "Batting_Avg", "Strike_Rate", "Runs", "Matches"]]).sum()
    )
    with st.spinner("Preparing ML model…"):
        ml = get_ml_results(df_hash, df.to_json())

    from config.constants import ML_FEATURES
    X_all_scaled = ml.scaler.transform(df[ML_FEATURES].copy())
    df["ML_Predicted_Form"] = ml.label_encoder.inverse_transform(ml.model.predict(X_all_scaled))
    df["ML_Confidence"] = ml.model.predict_proba(X_all_scaled).max(axis=1)

    # ====================================================================
    #  DASHBOARD
    # ====================================================================
    if selected == "Dashboard":
        top_scorer = df.nlargest(1, "Runs").iloc[0]
        country_count = df["Country"].nunique()
        avg_bat = df["Batting_Avg"].mean()
        avg_sr = df["Strike_Rate"].mean()

        st.markdown(tile_grid([
            tile("Total Players", len(df)),
            tile("Avg Batting Avg", f"{avg_bat:.1f}"),
            tile("🏆 Top Scorer", top_scorer["Player"], f"{int(top_scorer['Runs']):,} runs"),
            tile("Total Wickets", f"{df['Wickets'].sum():,}"),
            tile("Avg Strike Rate", f"{avg_sr:.1f}"),
            tile("🌍 Countries", country_count),
        ]), unsafe_allow_html=True)

        # Top Performers highlight card
        highlights = df.nlargest(3, "Impact_Score")
        medals = ["🥇", "🥈", "🥉"]
        hl_html = '<div class="card" style="margin-bottom:16px;"><h3>Top Performers</h3>'
        for i, (_, row) in enumerate(highlights.iterrows()):
            hl_html += (
                f'<div style="display:flex;justify-content:space-between;padding:6px 0;'
                f'border-bottom:1px solid {SURFACE};">'
                f'<span style="color:{TEXT};">{medals[i]} {html_escape(str(row["Player"]))} '
                f'<span style="color:{SECONDARY_TEXT};font-size:.8rem;">({html_escape(str(row["Country"]))})</span></span>'
                f'<span style="color:{ACCENT2};font-weight:600;">Impact: {row["Impact_Score"]:.1f}</span>'
                f'</div>'
            )
        hl_html += "</div>"
        st.markdown(hl_html, unsafe_allow_html=True)

        tab_overview, tab_scatter, tab_leaders = st.tabs(
            ["Performance Overview", "Scatter Analysis", "Leaderboard"]
        )

        with tab_overview:
            col1, col2 = st.columns(2)
            with col1:
                top15 = df.sort_values("Runs", ascending=False).head(15)
                fig = px.bar(
                    top15, x="Player", y="Runs", color="Form_Label",
                    title="Top 15 — Runs Scored",
                    color_discrete_map={"Good": ACCENT2, "Average": WARN, "Poor": DANGER},
                )
                fig.update_layout(xaxis_tickangle=-45, height=420, legend_title_text="Form")
                st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
            with col2:
                top_w = df.sort_values("Wickets", ascending=False).head(15)
                fig = px.bar(
                    top_w, x="Player", y="Wickets",
                    title="Top 15 — Wickets Taken",
                    color_discrete_sequence=[ACCENT],
                )
                fig.update_layout(xaxis_tickangle=-45, height=420)
                st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

        with tab_scatter:
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                min_matches = st.slider("Min Matches", 0, int(df["Matches"].max()), MIN_MATCHES_FILTER)
            with fc2:
                form_filter = st.multiselect(
                    "Form", ["Good", "Average", "Poor"],
                    default=["Good", "Average", "Poor"],
                )
            with fc3:
                country_filter = st.multiselect(
                    "Country", sorted(df["Country"].unique()),
                    default=sorted(df["Country"].unique()),
                )

            filtered = df[
                (df["Matches"] >= min_matches)
                & (df["Form_Label"].isin(form_filter))
                & (df["Country"].isin(country_filter))
            ]

            fig = px.scatter(
                filtered, x="Batting_Avg", y="Strike_Rate",
                color="Form_Label", size="Runs",
                title="Batting Average vs Strike Rate",
                hover_data=["Player", "Matches", "Wickets"],
                color_discrete_map={"Good": ACCENT2, "Average": WARN, "Poor": DANGER},
            )
            fig.update_layout(height=500)
            st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

            with st.expander("💡 Insight — Batting Average vs Strike Rate"):
                st.markdown(
                    f"**Filtered dataset:** {len(filtered)} players | "
                    f"**Avg Batting Avg:** {filtered['Batting_Avg'].mean():.1f} | "
                    f"**Avg SR:** {filtered['Strike_Rate'].mean():.1f}"
                )
                st.markdown(
                    "Players in the upper-right quadrant combine high consistency with aggressive scoring "
                    "— the most impactful profiles for limited-overs cricket."
                )

        with tab_leaders:
            leaders = df.nlargest(DEFAULT_LEADERBOARD_SIZE, "Impact_Score")[
                ["Player", "Country", "Matches", "Runs", "Batting_Avg",
                 "Strike_Rate", "Wickets", "Impact_Score", "Form_Label"]
            ].reset_index(drop=True)
            leaders.index = leaders.index + 1
            st.dataframe(
                leaders,
                use_container_width=True,
                height=600,
                column_config={
                    "Batting_Avg": st.column_config.NumberColumn("Bat Avg", format="%.1f"),
                    "Strike_Rate": st.column_config.NumberColumn("SR", format="%.1f"),
                    "Impact_Score": st.column_config.ProgressColumn(
                        "Impact Score", format="%.1f",
                        min_value=0, max_value=float(df["Impact_Score"].max()),
                    ),
                },
            )

    # ====================================================================
    #  PLAYER ANALYSIS
    # ====================================================================
    elif selected == "Player Analysis":
        st.markdown('<div class="section-title">Player Analysis</div>', unsafe_allow_html=True)

        fc1, fc2 = st.columns([2, 1])
        with fc2:
            all_countries = ["All Countries"] + sorted(df["Country"].unique())
            country_sel = st.selectbox(
                "Country Filter", all_countries,
                label_visibility="collapsed", key="pa_country",
            )
        
        # Filter players by country if a specific country is selected
        if country_sel != "All Countries":
            filtered_by_country = sorted(df[df["Country"] == country_sel]["Player"].tolist())
            pa_player_options = [p for p in filtered_by_country if p in player_options] or filtered_by_country
        else:
            pa_player_options = player_options
        
        with fc1:
            player_name = st.selectbox(
                "Select Player", pa_player_options,
                label_visibility="collapsed", index=0,
            )

        if player_name and len(pa_player_options) > 0:
            p = df[df["Player"] == player_name].iloc[0]
            tab_profile, tab_radar, tab_rank, tab_similar = st.tabs(
                ["Profile", "Radar Chart", "Ranking", "Similar Players"]
            )

            with tab_profile:
                col1, col2 = st.columns([1, 2])
                with col1:
                    card_html = (
                        '<div class="card">'
                        + f'<h3>{html_escape(str(player_name))}</h3>'
                        + f'<div style="margin-bottom:8px;">{form_badge(p["Form_Label"])}</div>'
                        + stat_row("Country", p["Country"])
                        + stat_row("Matches", int(p["Matches"]))
                        + stat_row("Runs", f"{int(p['Runs']):,}")
                        + stat_row("Batting Avg", f"{p['Batting_Avg']:.2f}")
                        + stat_row("Strike Rate", f"{p['Strike_Rate']:.2f}")
                        + stat_row("Wickets", int(p["Wickets"]))
                        + stat_row("Economy", f"{p['Economy']:.2f}")
                        + stat_row("Impact Score", f"{p['Impact_Score']:.2f}")
                    )
                    if int(p["Wickets"]) > 0:
                        card_html += (
                            f'<hr style="border-color:{SURFACE};margin:8px 0;">'
                            f'<div style="color:{SECONDARY_TEXT};font-size:.75rem;text-transform:uppercase;'
                            f'letter-spacing:.5px;margin-bottom:6px;">Bowling Profile</div>'
                            + stat_row("Economy Rate", f"{p['Economy']:.2f}")
                            + stat_row("Total Wickets", int(p["Wickets"]))
                        )
                    card_html += "</div>"
                    st.markdown(card_html, unsafe_allow_html=True)

                with col2:
                    rank_runs = int((df["Runs"] > p["Runs"]).sum() + 1)
                    rank_avg = int((df["Batting_Avg"] > p["Batting_Avg"]).sum() + 1)
                    rank_imp = int((df["Impact_Score"] > p["Impact_Score"]).sum() + 1)
                    st.markdown(tile_grid([
                        tile("Runs Rank", f"#{rank_runs}", f"of {len(df)}"),
                        tile("Batting Avg Rank", f"#{rank_avg}", f"of {len(df)}"),
                        tile("Impact Rank", f"#{rank_imp}", f"of {len(df)}"),
                    ]), unsafe_allow_html=True)

                    with st.expander("💡 Player Insight", expanded=True):
                        form = p["Form_Label"]
                        if form == "Good":
                            st.success(
                                f"{player_name} is in **excellent form** — batting average of "
                                f"{p['Batting_Avg']:.1f} with a strike rate of {p['Strike_Rate']:.1f}."
                            )
                        elif form == "Average":
                            st.warning(
                                f"{player_name} shows **moderate form**. Batting average of "
                                f"{p['Batting_Avg']:.1f} — room for improvement."
                            )
                        else:
                            st.error(
                                f"{player_name} is in a **lean patch** with a batting average of "
                                f"{p['Batting_Avg']:.1f}."
                            )

            with tab_radar:
                cats = ["Batting Avg", "Strike Rate", "Impact Score", "Matches", "Wickets"]
                max_wkt = df["Wickets"].max() or 1
                vals = [
                    p["Batting_Avg"] / (df["Batting_Avg"].max() or 1) * 100,
                    p["Strike_Rate"] / (df["Strike_Rate"].max() or 1) * 100,
                    p["Impact_Score"] / (df["Impact_Score"].max() or 1) * 100,
                    p["Matches"] / (df["Matches"].max() or 1) * 100,
                    p["Wickets"] / max_wkt * 100,
                ]
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=vals + [vals[0]], theta=cats + [cats[0]],
                    fill="toself", fillcolor="rgba(59,130,246,.15)",
                    line=dict(color=ACCENT, width=2), name=player_name,
                ))
                fig.update_layout(
                    title_text=f"{player_name} — Performance Radar",
                    polar=dict(
                        bgcolor="rgba(0,0,0,0)",
                        radialaxis=dict(visible=True, range=[0, 100], gridcolor=SURFACE, color=MUTED),
                        angularaxis=dict(gridcolor=SURFACE, color=MUTED),
                    ),
                    height=480, showlegend=False,
                )
                st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

            with tab_rank:
                rank_df = df[["Player", "Runs", "Batting_Avg", "Strike_Rate", "Wickets", "Impact_Score"]].copy()
                for c in ["Runs", "Batting_Avg", "Strike_Rate", "Wickets", "Impact_Score"]:
                    rank_df[f"{c}_Rank"] = rank_df[c].rank(ascending=False).astype(int)
                row = rank_df[rank_df["Player"] == player_name].iloc[0]
                st.markdown(tile_grid([
                    tile("Runs", f"#{int(row['Runs_Rank'])}"),
                    tile("Batting Avg", f"#{int(row['Batting_Avg_Rank'])}"),
                    tile("Strike Rate", f"#{int(row['Strike_Rate_Rank'])}"),
                    tile("Wickets", f"#{int(row['Wickets_Rank'])}"),
                    tile("Impact Score", f"#{int(row['Impact_Score_Rank'])}"),
                ]), unsafe_allow_html=True)

            with tab_similar:
                st.markdown('<div class="card"><h3>Players with Similar Profiles</h3></div>', unsafe_allow_html=True)
                try:
                    similar = find_similar_players(df, player_name, n=SIMILAR_PLAYERS_COUNT)
                    sim_cols = ["Player", "Country", "Batting_Avg", "Strike_Rate", "Wickets", "Impact_Score", "Form_Label"]
                    st.dataframe(similar[sim_cols], use_container_width=True)
                except Exception as exc:
                    st.markdown(empty_state("🔍", "Similar Player Lookup Unavailable", "Could not compute similar profiles for this player."), unsafe_allow_html=True)
                    logger.warning("find_similar_players failed: %s", exc)

    # ====================================================================
    #  CAREER TRAJECTORY
    # ====================================================================
    elif selected == "Career Trajectory":
        st.markdown('<div class="section-title">Career Trajectory</div>', unsafe_allow_html=True)

        player_name = st.selectbox("Select Player", player_options, key="traj_player")

        if player_name:
            p = df[df["Player"] == player_name].iloc[0]
            country = p["Country"]
            country_df = df[df["Country"] == country] if country != "Unknown" else df

            overall_rank = int((df["Impact_Score"] > p["Impact_Score"]).sum() + 1)
            country_rank = int((country_df["Impact_Score"] > p["Impact_Score"]).sum() + 1)
            runs_milestone = (int(p["Runs"]) // 1000) * 1000

            st.markdown(tile_grid([
                tile("Career Runs", f"{int(p['Runs']):,}"),
                tile("Batting Average", f"{p['Batting_Avg']:.1f}"),
                tile("Total Matches", int(p["Matches"])),
                tile("Wickets", int(p["Wickets"])),
                tile("Global Rank", f"#{overall_rank}", f"of {len(df)}"),
                tile("Country Rank", f"#{country_rank}", country),
            ]), unsafe_allow_html=True)

            tab_pct, tab_compare, tab_milestone = st.tabs(
                ["Percentile Rankings", "vs Averages", "Milestones"]
            )

            with tab_pct:
                stats_pct = {
                    "Runs":         float((df["Runs"] <= p["Runs"]).mean() * 100),
                    "Batting Avg":  float((df["Batting_Avg"] <= p["Batting_Avg"]).mean() * 100),
                    "Strike Rate":  float((df["Strike_Rate"] <= p["Strike_Rate"]).mean() * 100),
                    "Wickets":      float((df["Wickets"] <= p["Wickets"]).mean() * 100),
                    "Impact Score": float((df["Impact_Score"] <= p["Impact_Score"]).mean() * 100),
                }
                pct_df = pd.DataFrame({"Metric": list(stats_pct), "Percentile": list(stats_pct.values())})
                fig = px.bar(
                    pct_df, x="Percentile", y="Metric", orientation="h",
                    title=f"{player_name} — Percentile Rankings vs All Players",
                    color="Percentile",
                    color_continuous_scale=COLOR_SCALE_DIVERGING,
                    range_x=[0, 100],
                    labels={"Percentile": "Percentile Rank (%)"},
                )
                fig.add_vline(x=50, line_dash="dash", line_color=MUTED,
                              annotation_text="Median (50th)")
                fig.update_layout(height=420, showlegend=False)
                st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

                with st.expander("💡 Reading the chart"):
                    st.markdown(
                        "A **percentile rank of 80%** means the player outperforms 80% of all players "
                        "in that stat. The dashed median line divides below-average and above-average performers."
                    )

            with tab_compare:
                metrics = ["Batting_Avg", "Strike_Rate", "Runs", "Wickets"]
                cmp_rows = []
                for m in metrics:
                    label = m.replace("_", " ")
                    cmp_rows += [
                        {"Metric": label, "Group": player_name,          "Value": float(p[m])},
                        {"Metric": label, "Group": f"{country} Avg",     "Value": float(country_df[m].mean())},
                        {"Metric": label, "Group": "Global Avg",         "Value": float(df[m].mean())},
                    ]
                cmp_df = pd.DataFrame(cmp_rows)
                fig = px.bar(
                    cmp_df, x="Metric", y="Value", color="Group",
                    title=f"{player_name} vs Country Average vs Global Average",
                    barmode="group",
                    color_discrete_sequence=[ACCENT, ACCENT2, WARN],
                )
                fig.update_layout(height=420)
                st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

            with tab_milestone:
                wkt_milestone = (int(p["Wickets"]) // 50) * 50 if int(p["Wickets"]) >= 50 else 0
                country_avg_diff = p["Batting_Avg"] - country_df["Batting_Avg"].mean()
                global_avg_diff  = p["Batting_Avg"] - df["Batting_Avg"].mean()
                top25 = overall_rank <= (len(df) // 4)

                st.markdown(tile_grid([
                    tile("Runs Milestone",  f"{runs_milestone:,}+"),
                    tile("vs Country Avg",  f"{country_avg_diff:+.1f}", "batting avg"),
                    tile("vs Global Avg",   f"{global_avg_diff:+.1f}",  "batting avg"),
                    tile("Wicket Milestone", f"{wkt_milestone}+" if wkt_milestone else "—"),
                    tile("Top 25%?", "✅ Yes" if top25 else "❌ No", "by Impact Score"),
                ]), unsafe_allow_html=True)

                # Simulated cumulative runs progression
                matches_total = max(int(p["Matches"]), 1)
                runs_per_match = p["Runs"] / matches_total
                pts = list(range(0, matches_total + 1, max(1, matches_total // 20)))
                sim_df = pd.DataFrame({
                    "Matches Played": pts,
                    "Cumulative Runs": [int(x * runs_per_match) for x in pts],
                })
                fig = px.area(
                    sim_df, x="Matches Played", y="Cumulative Runs",
                    title=f"{player_name} — Simulated Cumulative Runs Progression",
                    color_discrete_sequence=[ACCENT],
                )
                fig.update_layout(height=380)
                st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
                st.caption("⚠️ Simulated from career average — not actual match-by-match data.")

    # ====================================================================
    #  HEAD-TO-HEAD
    # ====================================================================
    elif selected == "Head-to-Head":
        st.markdown('<div class="section-title">Head-to-Head Comparison</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            p1_name = st.selectbox("Player 1", player_options, key="h2h_p1")
        with col2:
            p2_opts = [p for p in player_options if p != p1_name]
            p2_name = st.selectbox("Player 2", p2_opts if p2_opts else player_options, key="h2h_p2")

        if p1_name and p2_name and p1_name != p2_name:
            p1 = df[df["Player"] == p1_name].iloc[0]
            p2 = df[df["Player"] == p2_name].iloc[0]

            tab_stats, tab_radar, tab_verdict = st.tabs(["Stat Delta", "Radar Overlay", "Verdict"])

            with tab_stats:
                comparison_stats = [
                    ("Runs", False), ("Batting_Avg", False), ("Strike_Rate", False),
                    ("Wickets", False), ("Economy", True), ("Matches", False), ("Impact_Score", False),
                ]
                rows = []
                for metric, lower_better in comparison_stats:
                    v1, v2 = float(p1[metric]), float(p2[metric])
                    if lower_better:
                        lead = p1_name if v1 < v2 else (p2_name if v2 < v1 else "Tied")
                    else:
                        lead = p1_name if v1 > v2 else (p2_name if v2 > v1 else "Tied")
                    rows.append({
                        "Stat": metric.replace("_", " "),
                        p1_name: f"{v1:.1f}",
                        p2_name: f"{v2:.1f}",
                        "Leader": lead,
                    })
                st.dataframe(pd.DataFrame(rows).set_index("Stat"), use_container_width=True)

            with tab_radar:
                cats = ["Batting Avg", "Strike Rate", "Impact Score", "Matches", "Wickets"]
                fig = go.Figure()
                for player, data, color in [(p1_name, p1, ACCENT), (p2_name, p2, ACCENT2)]:
                    vals = [
                        data["Batting_Avg"] / (df["Batting_Avg"].max() or 1) * 100,
                        data["Strike_Rate"] / (df["Strike_Rate"].max() or 1) * 100,
                        data["Impact_Score"] / (df["Impact_Score"].max() or 1) * 100,
                        data["Matches"] / (df["Matches"].max() or 1) * 100,
                        data["Wickets"] / (df["Wickets"].max() or 1) * 100,
                    ]
                    fig.add_trace(go.Scatterpolar(
                        r=vals + [vals[0]], theta=cats + [cats[0]],
                        fill="toself", name=player,
                        fillcolor=f"rgba({','.join(str(int(color[i:i+2], 16)) for i in (1,3,5))},.1)",
                        line=dict(color=color, width=2),
                    ))
                fig.update_layout(
                    title_text=f"{p1_name} vs {p2_name} — Radar Overlay",
                    polar=dict(
                        bgcolor="rgba(0,0,0,0)",
                        radialaxis=dict(visible=True, range=[0, 100], gridcolor=SURFACE, color=MUTED),
                        angularaxis=dict(gridcolor=SURFACE, color=MUTED),
                    ),
                    height=480,
                )
                st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

            with tab_verdict:
                weights = [
                    ("Batting_Avg", 0.30, False),
                    ("Strike_Rate", 0.20, False),
                    ("Runs",        0.25, False),
                    ("Wickets",     0.15, False),
                    ("Economy",     0.10, True),
                ]
                score_p1 = score_p2 = 0.0
                for metric, weight, lower_better in weights:
                    v1, v2 = float(p1[metric]), float(p2[metric])
                    total = v1 + v2
                    if total > 0:
                        if lower_better:
                            score_p1 += (1 - v1 / total) * weight * 100
                            score_p2 += (1 - v2 / total) * weight * 100
                        else:
                            score_p1 += (v1 / total) * weight * 100
                            score_p2 += (v2 / total) * weight * 100

                winner = p1_name if score_p1 >= score_p2 else p2_name
                st.markdown(tile_grid([
                    tile(p1_name[:24], f"{score_p1:.1f}", "Composite Score"),
                    tile("🏆 Winner", winner[:24]),
                    tile(p2_name[:24], f"{score_p2:.1f}", "Composite Score"),
                ]), unsafe_allow_html=True)

                verdict_df = pd.DataFrame({"Player": [p1_name, p2_name], "Score": [score_p1, score_p2]})
                fig = px.bar(
                    verdict_df, x="Player", y="Score",
                    title="Head-to-Head — Composite Score",
                    color="Player", text="Score",
                    color_discrete_sequence=[ACCENT, ACCENT2],
                )
                fig.update_traces(texttemplate="%{text:.1f}", textposition="inside")
                fig.update_layout(height=350, showlegend=False)
                st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

                with st.expander("📐 Scoring methodology"):
                    st.markdown(
                        "Composite score uses weighted stats:\n"
                        "- **Batting Avg** (30%) · **Runs** (25%) · **Strike Rate** (20%)\n"
                        "- **Wickets** (15%) · **Economy** (10%, lower = better)"
                    )

    # ====================================================================
    #  PLAYER COMPARISON
    # ====================================================================
    elif selected == "Player Comparison":
        st.markdown('<div class="section-title">Player Comparison</div>', unsafe_allow_html=True)

        selected_players = st.multiselect("Select 2–4 Players", player_options, max_selections=4)

        if len(selected_players) >= 2:
            cdf = df[df["Player"].isin(selected_players)]

            tab_table, tab_charts = st.tabs(["Comparison Table", "Visual Comparison"])

            with tab_table:
                display_cols = [
                    "Player", "Country", "Matches", "Runs", "Batting_Avg",
                    "Strike_Rate", "Wickets", "Economy", "Impact_Score", "Form_Label",
                ]
                st.dataframe(cdf[display_cols].set_index("Player"), use_container_width=True)

            with tab_charts:
                metric_choice = st.selectbox(
                    "Metric", ["Runs", "Batting_Avg", "Strike_Rate", "Wickets", "Economy", "Impact_Score"]
                )
                fig = px.bar(
                    cdf, x="Player", y=metric_choice, color="Player",
                    title=f"Player Comparison — {metric_choice}",
                    color_discrete_sequence=[ACCENT, ACCENT2, WARN, DANGER],
                )
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

                with st.expander("📊 Radar Overlay"):
                    cats = ["Batting Avg", "Strike Rate", "Impact Score", "Matches", "Wickets"]
                    fig = go.Figure()
                    colors = [ACCENT, ACCENT2, WARN, DANGER]
                    for idx, (_, row) in enumerate(cdf.iterrows()):
                        vals = [
                            row["Batting_Avg"] / (df["Batting_Avg"].max() or 1) * 100,
                            row["Strike_Rate"] / (df["Strike_Rate"].max() or 1) * 100,
                            row["Impact_Score"] / (df["Impact_Score"].max() or 1) * 100,
                            row["Matches"] / (df["Matches"].max() or 1) * 100,
                            row["Wickets"] / (df["Wickets"].max() or 1) * 100,
                        ]
                        c = colors[idx % len(colors)]
                        fig.add_trace(go.Scatterpolar(
                            r=vals + [vals[0]], theta=cats + [cats[0]],
                            fill="toself", name=row["Player"],
                            fillcolor=f"rgba({','.join(str(int(c[i:i+2], 16)) for i in (1,3,5))},.08)",
                            line=dict(color=c, width=2),
                        ))
                    fig.update_layout(
                        title_text="Player Comparison — Radar Overlay",
                        polar=dict(
                            bgcolor="rgba(0,0,0,0)",
                            radialaxis=dict(visible=True, range=[0, 100], gridcolor=SURFACE, color=MUTED),
                            angularaxis=dict(gridcolor=SURFACE, color=MUTED),
                        ),
                        height=480,
                    )
                    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

        elif len(selected_players) == 1:
            st.markdown(empty_state("👥", "Select More Players", "Select at least 2 players to compare."), unsafe_allow_html=True)
        else:
            st.markdown(empty_state("📊", "No Players Selected", "Choose 2–4 players from the dropdown to begin comparing."), unsafe_allow_html=True)

    # ====================================================================
    #  TEAM STATISTICS
    # ====================================================================
    elif selected == "Team Statistics":
        st.markdown('<div class="section-title">Team Statistics</div>', unsafe_allow_html=True)

        country_list = ["All Countries"] + sorted(df["Country"].unique())
        selected_country = st.selectbox("Select Country for Deep-Dive", country_list, key="ts_country")

        display_df = df if selected_country == "All Countries" else df[df["Country"] == selected_country]

        if selected_country != "All Countries" and not display_df.empty:
            best_bat = display_df.nlargest(1, "Batting_Avg").iloc[0]
            bowlers_  = display_df[display_df["Wickets"] > 0]
            best_bowl = bowlers_.nlargest(1, "Wickets").iloc[0] if not bowlers_.empty else None
            best_ar   = display_df.nlargest(1, "Impact_Score").iloc[0]
            tiles_list = [
                tile("🏏 Best Batsman", best_bat["Player"], f"Avg: {best_bat['Batting_Avg']:.1f}"),
                tile("⭐ Top Impact",   best_ar["Player"],  f"Score: {best_ar['Impact_Score']:.1f}"),
                tile("Players", len(display_df)),
            ]
            if best_bowl is not None:
                tiles_list.insert(1, tile("🎯 Best Bowler", best_bowl["Player"], f"{int(best_bowl['Wickets'])} wkts"))
            st.markdown(tile_grid(tiles_list), unsafe_allow_html=True)

        st.markdown(tile_grid([
            tile("Avg Matches",     f"{display_df['Matches'].mean():.0f}"),
            tile("Avg Runs",        f"{display_df['Runs'].mean():.0f}"),
            tile("Avg Batting Avg", f"{display_df['Batting_Avg'].mean():.1f}"),
            tile("Avg Strike Rate", f"{display_df['Strike_Rate'].mean():.1f}"),
            tile("Avg Wickets",     f"{display_df['Wickets'].mean():.0f}"),
            tile("Avg Economy",     f"{display_df['Economy'].mean():.1f}"),
        ]), unsafe_allow_html=True)

        tab_dist, tab_corr, tab_form = st.tabs(["Distributions", "Correlations", "Form Analysis"])

        with tab_dist:
            metric = st.selectbox(
                "Distribution of",
                ["Batting_Avg", "Strike_Rate", "Runs", "Wickets", "Economy"],
                key="dist_metric",
            )
            fig = px.histogram(
                display_df, x=metric, nbins=20, color_discrete_sequence=[ACCENT],
                title=f"Distribution of {metric.replace('_', ' ')}", marginal="box",
            )
            fig.update_layout(height=420)
            st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
            with st.expander("💡 Distribution Insight"):
                m = display_df[metric]
                st.markdown(
                    f"**Mean:** {m.mean():.2f} | **Median:** {m.median():.2f} | "
                    f"**Std Dev:** {m.std():.2f} | **Skew:** {m.skew():.2f}"
                )

        with tab_corr:
            corr_cols = ["Runs", "Batting_Avg", "Strike_Rate", "Wickets", "Economy", "Impact_Score"]
            fig = px.imshow(
                display_df[corr_cols].corr(), text_auto=".2f",
                title="Feature Correlation Matrix",
                color_continuous_scale=COLOR_SCALE_CORRELATION,
                aspect="auto",
            )
            fig.update_layout(height=500)
            st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

        with tab_form:
            col1, col2 = st.columns(2)
            with col1:
                form_counts = display_df["Form_Label"].value_counts()
                fig = px.pie(
                    values=form_counts.values, names=form_counts.index,
                    title="Player Form Distribution",
                    color=form_counts.index,
                    color_discrete_map={"Good": ACCENT2, "Average": WARN, "Poor": DANGER},
                    hole=0.45,
                )
                fig.update_layout(height=380)
                st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

            with col2:
                if selected_country == "All Countries":
                    cf = display_df.groupby(["Country", "Form_Label"]).size().reset_index(name="Count")
                    fig = px.bar(
                        cf, x="Country", y="Count", color="Form_Label",
                        title="Form Breakdown by Country", barmode="stack",
                        color_discrete_map={"Good": ACCENT2, "Average": WARN, "Poor": DANGER},
                    )
                    fig.update_layout(height=380, xaxis_tickangle=-45)
                else:
                    cats = ["Batting Avg", "Strike Rate", "Impact Score", "Matches", "Wickets"]
                    vals = [
                        display_df["Batting_Avg"].mean() / (df["Batting_Avg"].max() or 1) * 100,
                        display_df["Strike_Rate"].mean() / (df["Strike_Rate"].max() or 1) * 100,
                        display_df["Impact_Score"].mean() / (df["Impact_Score"].max() or 1) * 100,
                        display_df["Matches"].mean() / (df["Matches"].max() or 1) * 100,
                        display_df["Wickets"].mean() / (df["Wickets"].max() or 1) * 100,
                    ]
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=vals + [vals[0]], theta=cats + [cats[0]],
                        fill="toself", fillcolor="rgba(16,185,129,.15)",
                        line=dict(color=ACCENT2, width=2), name=selected_country,
                    ))
                    fig.update_layout(
                        title_text=f"{selected_country} — Team Radar",
                        polar=dict(
                            bgcolor="rgba(0,0,0,0)",
                            radialaxis=dict(visible=True, range=[0, 100], gridcolor=SURFACE, color=MUTED),
                            angularaxis=dict(gridcolor=SURFACE, color=MUTED),
                        ),
                        height=380,
                    )
                st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

    # ====================================================================
    #  DREAM XI BUILDER
    # ====================================================================
    elif selected == "Dream XI Builder":
        st.markdown('<div class="section-title">Dream XI Builder</div>', unsafe_allow_html=True)

        with st.expander("⚙️ Configure XI Composition", expanded=True):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                n_bat  = st.slider("Batsmen",         XI_MIN_BATSMEN, XI_MAX_BATSMEN, XI_DEFAULT_BATSMEN, key="xi_bat")
            with c2:
                n_ar   = st.slider("All-Rounders",    XI_MIN_ALLROUNDERS, XI_MAX_ALLROUNDERS, XI_DEFAULT_ALLROUNDERS, key="xi_ar")
            with c3:
                n_bowl = st.slider("Bowlers",         XI_MIN_BOWLERS, XI_MAX_BOWLERS, XI_DEFAULT_BOWLERS, key="xi_bowl")
            with c4:
                n_wk   = st.slider("Wicket-Keepers",  XI_MIN_WICKETKEEPERS, XI_MAX_WICKETKEEPERS, XI_DEFAULT_WICKETKEEPERS, key="xi_wk")

            total = n_bat + n_ar + n_bowl + n_wk
            if total != DREAM_XI_SIZE:
                st.warning(f"Total = **{total}** — must equal **{DREAM_XI_SIZE}** to build.")

            xi_countries = st.multiselect(
                "Filter by Country (optional)", sorted(df["Country"].unique()), key="xi_country"
            )

        if total == DREAM_XI_SIZE:
            pool = df.copy()
            if xi_countries:
                pool = pool[pool["Country"].isin(xi_countries)]

            if pool.empty:
                st.warning("No players found for the selected countries.")
            else:
                # Track config changes to auto-rebuild XI when sliders/country filters change
                current_config = (n_bat, n_ar, n_bowl, n_wk, tuple(sorted(xi_countries)))
                if "xi_config" not in st.session_state:
                    st.session_state["xi_config"] = None
                
                config_changed = st.session_state["xi_config"] != current_config
                button_clicked = st.button("🎲 Regenerate XI", key="regen_xi")
                
                if button_clicked or config_changed:
                    st.session_state["xi_config"] = current_config
                    with st.spinner("Building Dream XI…"):
                        ar_pool   = pool[(pool["Wickets"] >= 30) & (pool["Batting_Avg"] >= 25)]
                        bow_pool  = pool[pool["Wickets"] >= 50]

                        ar_pick   = ar_pool.nlargest(n_ar, "Impact_Score").head(n_ar)
                        used      = set(ar_pick["Player"])

                        bow_cands = bow_pool[~bow_pool["Player"].isin(used)]
                        bow_pick  = bow_cands.nlargest(n_bowl, "Wickets").head(n_bowl)
                        used     |= set(bow_pick["Player"])

                        wk_cands  = pool[~pool["Player"].isin(used)]
                        wk_pick   = wk_cands.nlargest(n_wk, "Strike_Rate").head(n_wk)
                        used     |= set(wk_pick["Player"])

                        bat_cands = pool[~pool["Player"].isin(used)]
                        bat_pick  = bat_cands.nlargest(n_bat, "Batting_Avg").head(n_bat)

                        xi = pd.concat([bat_pick, ar_pick, bow_pick, wk_pick]).drop_duplicates(subset="Player")

                        if len(xi) < DREAM_XI_SIZE:
                            extra = pool[~pool["Player"].isin(xi["Player"])].nlargest(
                                DREAM_XI_SIZE - len(xi), "Impact_Score"
                            )
                            xi = pd.concat([xi, extra]).drop_duplicates(subset="Player").head(DREAM_XI_SIZE)

                        xi = xi.head(DREAM_XI_SIZE).reset_index(drop=True)
                        
                        # Assign roles based on order: batsmen, all-rounders, bowlers, WK
                        roles = []
                        for idx, (_, row) in enumerate(xi.iterrows()):
                            player_in_bat = row["Player"] in bat_pick["Player"].values if not bat_pick.empty else False
                            player_in_ar  = row["Player"] in ar_pick["Player"].values if not ar_pick.empty else False
                            player_in_bow = row["Player"] in bow_pick["Player"].values if not bow_pick.empty else False
                            player_in_wk  = row["Player"] in wk_pick["Player"].values if not wk_pick.empty else False
                            
                            if player_in_ar:
                                roles.append("All-Rounder")
                            elif player_in_bow:
                                roles.append("Bowler")
                            elif player_in_wk:
                                roles.append("WK")
                            elif player_in_bat:
                                roles.append("Batsman")
                            else:
                                roles.append("Utility")
                        
                        xi["Role"] = roles
                        st.session_state["xi_players"] = xi

                xi = st.session_state.get("xi_players", pd.DataFrame())

                if not xi.empty:
                    st.markdown(tile_grid([
                        tile("Team Impact Score", f"{xi['Impact_Score'].sum():.1f}"),
                        tile("Avg Batting Avg",   f"{xi['Batting_Avg'].mean():.1f}"),
                        tile("Avg Strike Rate",   f"{xi['Strike_Rate'].mean():.1f}"),
                        tile("Wickets Pool",       int(xi["Wickets"].sum())),
                        tile("Countries",          xi["Country"].nunique()),
                    ]), unsafe_allow_html=True)

                    show_cols = ["Player", "Country", "Role", "Batting_Avg", "Strike_Rate", "Wickets", "Impact_Score", "Form_Label"]
                    show_cols = [c for c in show_cols if c in xi.columns]
                    st.dataframe(xi[show_cols], use_container_width=True, height=420)

                    st.download_button(
                        "📥 Export Dream XI as CSV",
                        xi.to_csv(index=False),
                        "dream_xi.csv", "text/csv",
                    )

                    with st.expander("💡 How are players selected?"):
                        st.markdown(
                            "The Dream XI algorithm picks players in this order:\n\n"
                            "1. **All-Rounders** — ranked by Impact Score (batting avg ≥ 25 & wickets ≥ 30)\n"
                            "2. **Bowlers** — ranked by total Wickets (wickets ≥ 50)\n"
                            "3. **Wicket-Keepers** — ranked by Strike Rate\n"
                            "4. **Batsmen** — ranked by Batting Average\n\n"
                            "If not enough specialist players are available, remaining slots "
                            "are filled by highest Impact Score from the pool."
                        )

    # ====================================================================
    #  ML PREDICTION
    # ====================================================================
    elif selected == "ML Prediction":
        st.markdown('<div class="section-title">ML-Powered Form Prediction</div>', unsafe_allow_html=True)

        match_rate = ((df["Form_Label"] == df["ML_Predicted_Form"]).sum() / len(df)) * 100
        st.markdown(tile_grid([
            tile("Algorithm",  "Logistic Reg."),
            tile("Accuracy",   f"{ml.accuracy*100:.1f}%"),
            tile("CV Accuracy",f"{ml.cv_accuracy_mean*100:.1f}%"),
            tile("F1 Score",   f"{ml.f1*100:.1f}%"),
            tile("Precision",  f"{ml.precision*100:.1f}%"),
            tile("Recall",     f"{ml.recall*100:.1f}%"),
            tile("Match Rate", f"{match_rate:.1f}%"),
            tile("Features",   "4"),
        ]), unsafe_allow_html=True)

        tab_pred, tab_cm, tab_feat, tab_report = st.tabs(
            ["Predictions", "Confusion Matrix", "Feature Importance", "Classification Report"]
        )

        with tab_pred:
            pred_df = df[["Player", "Batting_Avg", "Strike_Rate", "Runs", "Matches",
                          "Form_Label", "ML_Predicted_Form", "ML_Confidence"]].copy()
            pred_df["Match"] = (pred_df["Form_Label"] == pred_df["ML_Predicted_Form"]).map(
                {True: "✅", False: "❌"}
            )
            pred_df["ML_Confidence"] = pred_df["ML_Confidence"].apply(lambda x: f"{x:.1%}")
            pred_df.columns = [
                "Player", "Bat Avg", "SR", "Runs", "Matches",
                "Rule-Based", "ML Predicted", "Confidence", "Match",
            ]
            st.dataframe(pred_df, use_container_width=True, height=500)

        with tab_cm:
            cm = confusion_matrix(ml.y_test, ml.y_pred)
            labels = ml.label_encoder.inverse_transform(np.unique(ml.y_test))
            fig = px.imshow(
                cm, text_auto=True, x=labels, y=labels,
                title="Confusion Matrix — ML Form Prediction",
                color_continuous_scale=COLOR_SCALE_SEQUENTIAL,
                labels=dict(x="Predicted", y="Actual"),
            )
            fig.update_layout(height=440)
            st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

        with tab_feat:
            feature_names = ["Batting_Avg", "Strike_Rate", "Runs", "Matches"]
            for idx, class_name in enumerate(ml.label_encoder.classes_):
                with st.expander(f"Coefficients — {class_name} class", expanded=(idx == 0)):
                    fig = px.bar(
                        x=feature_names, y=ml.model.coef_[idx],
                        title=f"Feature Coefficients — {class_name}",
                        color=ml.model.coef_[idx],
                        color_continuous_scale=[DANGER, SURFACE, ACCENT2],
                        labels={"x": "Feature", "y": "Coefficient"},
                    )
                    fig.update_layout(height=320, showlegend=False)
                    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)

        with tab_report:
            st.markdown('<div class="card"><h3>Classification Report</h3></div>', unsafe_allow_html=True)
            st.code(ml.class_report)

    # ====================================================================
    #  MATCH PREDICTION
    # ====================================================================
    elif selected == "Match Prediction":
        st.markdown('<div class="section-title">Match Prediction</div>', unsafe_allow_html=True)

        st.info(
            "⚠️ Statistical model based on individual player stats "
            "(batting strength + bowling strength via Impact Scores). Not an actual match simulation."
        )

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                '<div class="team-label team-label-a">🔵 Team A</div>',
                unsafe_allow_html=True,
            )
            team_a = st.multiselect(
                "Team A (up to 11)", df["Player"].sort_values().tolist(),
                max_selections=11, key="match_a",
            )
        with c2:
            st.markdown(
                '<div class="team-label team-label-b">🟢 Team B</div>',
                unsafe_allow_html=True,
            )
            team_b = st.multiselect(
                "Team B (up to 11)", df["Player"].sort_values().tolist(),
                max_selections=11, key="match_b",
            )

        if len(team_a) >= MIN_TEAM_SIZE and len(team_b) >= MIN_TEAM_SIZE:
            str_a = compute_team_strength(df, team_a)
            str_b = compute_team_strength(df, team_b)
            total = str_a["overall_strength"] + str_b["overall_strength"]
            prob_a = str_a["overall_strength"] / total if total > 0 else 0.5
            prob_b = str_b["overall_strength"] / total if total > 0 else 0.5

            st.markdown(tile_grid([
                tile("Team A Batting",  f"{str_a['batting_strength']:.1f}"),
                tile("Team A Bowling",  f"{str_a['bowling_strength']:.1f}"),
                tile("Team B Batting",  f"{str_b['batting_strength']:.1f}"),
                tile("Team B Bowling",  f"{str_b['bowling_strength']:.1f}"),
            ]), unsafe_allow_html=True)

            pc1, pc2 = st.columns(2)
            with pc1:
                st.metric("Team A Win Probability", f"{prob_a:.1%}")
                st.progress(float(prob_a))
            with pc2:
                st.metric("Team B Win Probability", f"{prob_b:.1%}")
                st.progress(float(prob_b))

            winner = "Team A" if prob_a > prob_b else ("Team B" if prob_b > prob_a else "Tied")
            st.markdown(
                f'<div class="verdict-card">'
                f'<h3>🏆 Predicted Winner: {winner}</h3>'
                f'<p style="color:{MUTED};font-size:.9rem;">Based on composite batting + bowling strength</p>'
                f'</div>',
                unsafe_allow_html=True,
            )

            with st.expander("📊 Top Contributors"):
                ta_top = df[df["Player"].isin(team_a)].nlargest(TOP_CONTRIBUTORS_COUNT, "Impact_Score")[
                    ["Player", "Batting_Avg", "Strike_Rate", "Wickets", "Impact_Score"]
                ].reset_index(drop=True)
                tb_top = df[df["Player"].isin(team_b)].nlargest(TOP_CONTRIBUTORS_COUNT, "Impact_Score")[
                    ["Player", "Batting_Avg", "Strike_Rate", "Wickets", "Impact_Score"]
                ].reset_index(drop=True)
                cc1, cc2 = st.columns(2)
                with cc1:
                    st.markdown("**🔵 Team A — Top 5**")
                    st.dataframe(ta_top, use_container_width=True)
                with cc2:
                    st.markdown("**🟢 Team B — Top 5**")
                    st.dataframe(tb_top, use_container_width=True)

        elif team_a or team_b:
            st.info(
                f"Add at least **{MIN_TEAM_SIZE} players** to each team. "
                f"(Team A: {len(team_a)}, Team B: {len(team_b)})"
            )
        else:
            st.markdown(empty_state("🏏", "Select Teams to Predict", "Select up to 11 players for each team to predict the match outcome."), unsafe_allow_html=True)

    # ====================================================================
    #  SETTINGS
    # ====================================================================
    elif selected == "Settings":
        st.markdown('<div class="section-title">Settings & Info</div>', unsafe_allow_html=True)

        tab_about, tab_data, tab_quality = st.tabs(["About", "Dataset", "Data Quality"])

        with tab_about:
            st.markdown(
                '<div class="card">'
                '<h3>About Cricklytics Pro</h3>'
                '<p class="about-text">'
                'Cricklytics Pro is a professional-grade cricket analytics dashboard combining real-time data, '
                'advanced visualisations and machine-learning predictions. Built for TY final year project.'
                '</p></div>',
                unsafe_allow_html=True,
            )
            st.markdown(tile_grid([
                tile("Frontend",  "Streamlit"),
                tile("ML Engine", "Scikit-learn"),
                tile("Viz",       "Plotly"),
                tile("Data",      "Pandas & NumPy"),
                tile("Pages",     "10"),
                tile("ML Features", "4"),
            ]), unsafe_allow_html=True)

            with st.expander("🗺 Roadmap"):
                st.markdown(
                    "- ✅ Player Analysis with Similar Players\n"
                    "- ✅ Career Trajectory — Percentile Rankings\n"
                    "- ✅ Head-to-Head Comparison\n"
                    "- ✅ Dream XI Builder\n"
                    "- ✅ Match Prediction Model\n"
                    "- ✅ ML Prediction with Cross-Validation\n"
                    "- 🔜 PDF Report Export\n"
                    "- 🔜 Real-time Match Scorecard Integration"
                )

        with tab_data:
            csv_path = Path(CSV_FILE_PATH)
            if csv_path.exists():
                last_mod = datetime.fromtimestamp(csv_path.stat().st_mtime).strftime("%d %b %Y, %H:%M:%S")
                file_kb = csv_path.stat().st_size / 1024
                st.markdown(tile_grid([
                    tile("CSV File",      csv_path.name),
                    tile("Players",       len(df)),
                    tile("Last Modified", last_mod),
                    tile("File Size",     f"{file_kb:.1f} KB"),
                ]), unsafe_allow_html=True)

            api_key = os.getenv("CRICKETDATA_API_KEY")
            if api_key:
                if st.button("🔄 Refresh Data from CricAPI", key="refresh_api_btn"):
                    with st.spinner("Fetching latest data from CricAPI… (30–60 seconds)"):
                        ok, msg = refresh_csv_from_api(api_key)
                    if ok:
                        st.success(f"✅ {msg}")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"❌ Refresh failed: {msg}")
            else:
                st.caption("💡 Set `CRICKETDATA_API_KEY` in your `.env` file to enable live data refresh.")

            st.markdown('<div class="card"><h3>Dataset Preview</h3></div>', unsafe_allow_html=True)
            st.dataframe(df.head(15), use_container_width=True)
            st.download_button(
                "📥 Download Full Dataset",
                df.to_csv(index=False),
                "cricklytics_export.csv", "text/csv",
            )

        with tab_quality:
            st.markdown('<div class="card"><h3>Data Quality Report</h3></div>', unsafe_allow_html=True)
            numeric_cols = ["Matches", "Runs", "Batting_Avg", "Strike_Rate", "Wickets", "Economy"]
            qrows = []
            completeness_vals = []
            for col in numeric_cols:
                if col in df.columns:
                    non_zero = int((df[col] != 0).sum())
                    pct = non_zero / len(df) * 100
                    qrows.append({
                        "Column": col,
                        "Non-Zero": non_zero,
                        "% Complete": f"{pct:.1f}%",
                        "Min": f"{df[col].min():.1f}",
                        "Max": f"{df[col].max():.1f}",
                        "Mean": f"{df[col].mean():.1f}",
                    })
                    completeness_vals.append(pct)
            st.dataframe(pd.DataFrame(qrows), use_container_width=True)

            fig = px.bar(
                x=numeric_cols, y=completeness_vals,
                title="Data Completeness by Column (%)",
                color_discrete_sequence=[ACCENT2],
                labels={"x": "Column", "y": "Completeness (%)"},
            )
            fig.update_layout(height=320, yaxis_range=[0, 105])
            st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)


# ============================================================================
# RUN APPLICATION
# ============================================================================
if __name__ == "__main__":
    main()
