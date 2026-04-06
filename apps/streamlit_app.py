"""Basic Streamlit UI for Diamond RCA.

Designed as a thin presentation layer over `diamond_rca.ui.service` so the same
business logic can move behind a future REST API for a React frontend.
"""

from __future__ import annotations

import streamlit as st

from diamond_rca.rca.fishbone import Fishbone, default_categories
from diamond_rca.rca.five_whys import build_five_whys
from diamond_rca.rca.framework import RCAReport
from diamond_rca.ui.service import build_collapse_analysis
from diamond_rca.viz.plots import plot_rolling_metric

st.set_page_config(page_title="Diamond RCA", layout="wide")
st.title("Diamond RCA: Baseball Collapse Explorer")
st.caption("Streamlit starter UI (upgrade-friendly toward a future React frontend).")

with st.sidebar:
    st.header("Analysis Controls")
    team = st.text_input("Team", value="NYM").strip().upper() or "NYM"
    season = st.number_input("Season", min_value=2000, max_value=2100, value=2025, step=1)
    window = st.slider("Rolling window", min_value=5, max_value=40, value=20)
    threshold = st.slider("Collapse threshold", min_value=0.10, max_value=0.70, value=0.35)
    run_button = st.button("Run analysis", type="primary")

if run_button:
    result = build_collapse_analysis(
        team=team, season=int(season), window=window, threshold=threshold
    )

    st.subheader("Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Games", result.total_games)
    c2.metric("Collapse-flagged games", result.collapse_games)
    c3.metric("Collapse rate", f"{result.collapse_rate:.1%}")

    if result.games.empty:
        st.warning("No data returned. Try a different team/season or check your network.")
        st.stop()

    st.subheader("Rolling win percentage")
    chart_df = result.games.reset_index(drop=True).copy()
    chart_df["game_number"] = chart_df.index + 1
    fig, _ = plot_rolling_metric(
        chart_df,
        x_col="game_number",
        y_col="rolling_win_pct",
        title=f"{team} {season} Rolling Win% ({window}-game)",
    )
    st.pyplot(fig, use_container_width=True)

    st.subheader("Game table")
    cols = [
        "game_date",
        "opponent",
        "result",
        "runs_for",
        "runs_against",
        "rolling_win_pct",
        "is_collapse_window",
    ]
    display_cols = [col for col in cols if col in chart_df.columns]
    st.dataframe(chart_df[display_cols], use_container_width=True)

    st.subheader("RCA draft (Markdown)")
    problem = st.text_input(
        "Problem statement",
        value=f"{team} {season} experienced a sustained underperformance window.",
    )
    answers_text = st.text_area(
        "5 Whys answers (one per line)",
        value="Bullpen performance declined in high leverage.\nStarter depth was strained.\nOffense underperformed with runners in scoring position.",
        height=120,
    )

    answers = [line.strip() for line in answers_text.splitlines() if line.strip()]
    fishbone = Fishbone(effect=problem)
    for category in default_categories():
        fishbone.add_cause(category, "Add evidence-backed cause here")

    report = RCAReport(
        problem_statement=problem,
        five_whys=build_five_whys(problem, answers),
        fishbone=fishbone,
    )
    markdown = report.to_markdown(title=f"{team} {season} Collapse RCA Draft")
    st.code(markdown, language="markdown")
