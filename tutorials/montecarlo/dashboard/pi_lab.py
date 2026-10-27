"""Lesson 2: one dartboard experiment, with the arithmetic exposed."""

from __future__ import annotations

import math

import streamlit as st

from dashboard.figures import dartboard_figure, running_figure
from dashboard.theme import lesson_banner, next_lesson, show
from montecarlo.pi import estimate_pi, explain_estimate, running_estimate

_DISPLAY_CAP = 2_500


@st.cache_data(show_spinner=False)
def _load_pi(n: int, seed: int):
    return estimate_pi(n, seed)


def _seed() -> int:
    if "pi_seed" not in st.session_state:
        st.session_state.pi_seed = 7
    if st.button("Redraw", type="primary", key="new_darts"):
        st.session_state.pi_seed += 1
    return int(st.session_state.pi_seed)


def page() -> None:
    st.header("Throwing darts at π")
    lesson_banner(
        "The estimate is 4 times the fraction of darts that landed in the quarter disk. "
        "Move the count back to 1: a single dart estimates π as 0 or as 4."
    )

    controls = st.columns((1.15, 1.25, 0.7))
    with controls[0]:
        n = st.slider("Darts drawn", min_value=100, max_value=20_000, value=2_000, step=100)
    with controls[2]:
        seed = _seed()
        st.caption(f"Seed {seed}")

    if st.session_state.get("scrub_owner") != n:
        st.session_state.scrub_owner = n
        st.session_state.darts_counted = n
    with controls[1]:
        k = st.slider(
            "Darts counted, a prefix of those draws",
            min_value=1,
            max_value=n,
            key="darts_counted",
            help="The draws stay fixed while you move this. You are choosing how much of one sample to average.",
        )

    experiment = _load_pi(n, seed).prefix(k)
    path = running_estimate(experiment.inside)
    true_se = experiment.true_standard_error
    z_distance = (experiment.estimate - math.pi) / true_se

    metrics = st.columns(3)
    low_text, high_text = _interval_ends(experiment)
    metrics[0].metric("Estimate of π", f"{experiment.estimate:.4f}")
    metrics[1].metric("Absolute error", f"{abs(experiment.estimate - math.pi):.4f}")
    metrics[2].metric("Standard error", f"{experiment.standard_error:.4f}")
    st.markdown(f"**95% interval: [{low_text}, {high_text}]**")
    st.caption(
        f"Using the first {k:,} of {n:,} darts, {experiment.hits:,} landed inside. "
        f"This run sits {abs(z_distance):.2f} true standard errors from π. "
        f"A distance near 1 is ordinary for one experiment; past about 2 is uncommon. "
        f"That yardstick uses the known value of π, so it is a check. "
        f"The interval above uses only the sample."
    )
    if experiment.hits in (0, experiment.n):
        st.caption(
            "Every counted dart landed on the same side of the arc, so the sample "
            "standard error is 0 and the interval collapses to a point. That is a "
            "small-sample failure of the estimated interval. The shaded band on the "
            "path uses the true standard error and stays open."
        )

    board, path_col = st.columns(2, gap="large")
    with board:
        shown = min(_DISPLAY_CAP, experiment.n)
        show(dartboard_figure(experiment.x[:shown], experiment.y[:shown], experiment.inside[:shown]))
        if shown < experiment.n:
            st.caption(f"The cloud shows the first {shown:,} darts. The estimate counts all {experiment.n:,}.")
        else:
            st.caption("The cloud shows every dart being counted.")
    with path_col:
        show(running_figure(path))
        st.caption(
            "The shaded band marks, at each n, where about 95% of experiments land. "
            "The vertical scale is that band at the current count, so move the count "
            "back toward 1 and the scale opens onto estimates of 0 and 4. "
            "An ordinary path steps outside the band along the way. The band uses the true π as a teaching overlay."
        )

    st.subheader("The arithmetic")
    st.code(explain_estimate(experiment), language="text")
    st.caption("Same operations as estimate_pi and PiResult.standard_error in montecarlo/pi.py.")
    st.subheader("The first darts")
    st.dataframe(_first_rows(experiment), hide_index=True, width="stretch")
    st.caption("The running estimate multiplies the fraction of hits so far by 4. After one dart it is 0 or 4.")

    with st.expander("Source: estimate_pi"):
        import inspect

        st.code(inspect.getsource(estimate_pi), language="python")

    next_lesson("The slow square root")


def _interval_ends(experiment) -> tuple[str, str]:
    from montecarlo.pi import confidence_interval

    low, high = confidence_interval(experiment.estimate, experiment.standard_error)
    return f"{low:.3f}", f"{high:.3f}"


def _first_rows(experiment, rows: int = 8) -> list[dict[str, object]]:
    count = min(rows, experiment.n)
    path = running_estimate(experiment.inside[:count])
    table = []
    for i in range(count):
        radius = float(experiment.x[i] ** 2 + experiment.y[i] ** 2)
        table.append(
            {
                "Dart": i + 1,
                "x": round(float(experiment.x[i]), 4),
                "y": round(float(experiment.y[i]), 4),
                "x² + y²": round(radius, 4),
                "Inside": "yes" if bool(experiment.inside[i]) else "no",
                "Running π̂": round(float(path[i]), 4),
            }
        )
    return table
