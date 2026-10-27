"""Lesson 3: the sampling distribution, the 1/√n law, and coverage."""

from __future__ import annotations

import streamlit as st

from dashboard.figures import coverage_figure, error_figure, spread_figure
from dashboard.theme import lesson_banner, next_lesson, show
from montecarlo.convergence import convergence_grid, interval_coverage
from montecarlo.pi import ERROR_CONSTANT

TEACHING_SIZES = (50, 200, 800, 3_200, 12_800)
BOX_REPLICATIONS = 300
COVERAGE_REPLICATIONS = 400
_SHOW_INTERVALS = 36


@st.cache_data(show_spinner="Running a few hundred experiments at each sample size…")
def _load_grid(seed: int):
    return convergence_grid(TEACHING_SIZES, BOX_REPLICATIONS, seed)


@st.cache_data(show_spinner="Building confidence intervals…")
def _load_coverage(n: int, seed: int):
    return interval_coverage(n, COVERAGE_REPLICATIONS, seed)


def _seed() -> int:
    if "conv_seed" not in st.session_state:
        st.session_state.conv_seed = 19
    if st.button("New batch of experiments", type="primary", key="new_batch"):
        st.session_state.conv_seed += 1
    return int(st.session_state.conv_seed)


def page() -> None:
    st.header("The slow square root")
    lesson_banner(
        "The typical error shrinks like 1/√n. "
        "A 95% interval is a statement about many experiments, and you can count how often it holds."
    )

    seed = _seed()
    st.caption(f"Seed {seed}. Each step below multiplies the throws by 4, which halves the theoretical standard error.")

    grid = _load_grid(seed)
    st.subheader("The sampling distribution of one estimate")
    st.markdown(
        f"""
Each box is **{BOX_REPLICATIONS} separate experiments**. A single experiment
produces one dot that could have been drawn from that box. The box shrinks
because the standard error shrinks, and it shrinks around π because the
estimator is unbiased: the expected value of π̂ is π at every sample size.
        """
    )
    show(spread_figure(grid))

    st.subheader("Measured error against the formula")
    st.markdown(
        f"""
$C = 4\\sqrt{{p(1-p)}} = {ERROR_CONSTANT:.3f}$, with $p=\\pi/4$.
The theory says the standard error is $C/\\sqrt{{n}}$.
The dotted line falls like $1/n$, starting from the same first point, so the
slower square-root rate has something to be compared with.
The lower panel multiplies the measured error by $\\sqrt{{n}}$. The square-root
law says that product stays near $C$.
        """
    )
    show(error_figure(grid))

    table = []
    for i, n in enumerate(grid.sample_sizes):
        table.append(
            {
                "Throws": f"{int(n):,}",
                "Theoretical SE": f"{grid.theoretical_se[i]:.4f}",
                "Empirical RMSE": f"{grid.rmse[i]:.4f}",
                "Empirical SD": f"{grid.empirical_sd[i]:.4f}",
                "RMSE × √n": f"{grid.error_times_sqrt_n[i]:.3f}",
            }
        )
    st.dataframe(table, hide_index=True, width="stretch")
    st.caption(
        "Theoretical SE is C/√n. Empirical RMSE is the square root of the average "
        "squared error across the experiments in the box. Empirical SD is their "
        "sample standard deviation. For this unbiased estimator those two spreads "
        "agree, up to the noise of having finitely many boxes. "
        "Click “New batch”. The boxes move. RMSE × √n stays near "
        f"{ERROR_CONSTANT:.2f}."
    )

    st.subheader("What a 95% interval claims")
    st.markdown(
        """
Take many experiments. In each one, build the interval you could report
without knowing π: estimate ± z × (sample standard error), with z from
SciPy's normal quantile. Then check, using the known π, whether the interval
contained it. The coverage is that success rate. The claim "95%" is a claim
about this procedure, measured over experiments. One particular interval
either contains π or it does not.
        """
    )
    n_interval = st.slider(
        "Throws inside each interval experiment",
        min_value=30,
        max_value=4_000,
        value=1_000,
        step=10,
        help="Near 1,000 the normal approximation is comfortable. Near 30 it starts to fray.",
    )
    coverage = _load_coverage(n_interval, seed)
    rate_cols = st.columns(3)
    rate_cols[0].metric("Nominal coverage", "95%")
    rate_cols[1].metric("Measured coverage", f"{coverage.coverage:.1%}")
    rate_cols[2].metric("Intervals checked", f"{coverage.replications:,}")
    if coverage.degenerate:
        st.caption(
            f"In {coverage.degenerate} experiments the sample standard error was 0, "
            "because every dart landed on the same side of the arc. Those intervals "
            "are a single point. The normal recipe needs the sample to show some variation."
        )
    show(coverage_figure(coverage, _SHOW_INTERVALS))
    st.caption(
        f"The chart draws {_SHOW_INTERVALS} of the {coverage.replications} intervals. "
        "The measured coverage uses every interval. Teal segments contain π. "
        "Orange segments miss it. Drag the throw count down toward 30 and run a "
        "new batch: small samples are skewed yes/no averages, and the normal interval is an approximation that improves as n grows."
    )

    next_lesson("A deadline you can miss")
