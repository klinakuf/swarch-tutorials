"""Streamlit dashboard for the Monte Carlo tutorial.

Run from this tutorial folder:

    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from dashboard.convergence_lab import page as page_convergence
from dashboard.decision import page as page_decision
from dashboard.implications import page as page_implications
from dashboard.pi_lab import page as page_pi
from dashboard.theme import inject_css, sidebar
from dashboard.theory import page as page_theory


def main() -> None:
    st.set_page_config(
        page_title="Monte Carlo, from one picture",
        page_icon="◎",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()
    lesson = sidebar()
    pages = {
        "The idea": page_theory,
        "Throwing darts at π": page_pi,
        "The slow square root": page_convergence,
        "A deadline you can miss": page_decision,
        "What to take with you": page_implications,
    }
    pages[lesson]()


main()
