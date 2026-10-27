"""Shared color and page chrome for the dashboard."""

from __future__ import annotations

import streamlit as st

INSIDE = "#0f766e"
OUTSIDE = "#c2410c"
TRUTH = "#1d4ed8"
GOLD = "#b45309"
INK = "#1c2430"
MUTED = "#5c6b7a"
BAND = "rgba(29, 78, 216, 0.16)"
GRID = "#e6e2da"

LESSONS: tuple[str, ...] = (
    "The idea",
    "Throwing darts at π",
    "The slow square root",
    "A deadline you can miss",
    "What to take with you",
)

_CSS = """
<style>
.block-container {
  padding-top: 1.25rem;
  padding-bottom: 2.5rem;
  max-width: 1080px;
}
.callout {
  background: #efece6;
  border-left: 4px solid #0f766e;
  padding: 0.75rem 1rem;
  border-radius: 0 10px 10px 0;
  margin: 0.2rem 0 1rem;
  color: #1c2430;
  line-height: 1.5;
}
div[data-testid="stMetricValue"] {
  font-variant-numeric: tabular-nums;
}
div[data-testid="stCode"] pre {
  white-space: pre-wrap !important;
}
</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def lesson_banner(text: str) -> None:
    st.markdown(f'<div class="callout">{text}</div>', unsafe_allow_html=True)


def sidebar() -> str:
    st.sidebar.markdown("## Monte Carlo")
    st.sidebar.caption("One picture, then a decision.")
    choice = st.sidebar.radio("Lessons", LESSONS, label_visibility="collapsed")
    st.sidebar.divider()
    st.sidebar.caption(
        "NumPy draws the samples. SciPy supplies the normal quantile and the "
        "triangular durations. Plotly draws the figures."
    )
    return choice


def show(fig, *, stretch: bool = True) -> None:
    st.plotly_chart(
        fig,
        width="stretch" if stretch else "content",
        config={
            "displaylogo": False,
            "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        },
    )


def next_lesson(name: str) -> None:
    st.divider()
    st.caption(f"Next lesson, in the sidebar: {name}.")
