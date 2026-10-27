"""Lesson 4: a deadline probability for three triangular tasks."""

from __future__ import annotations

import streamlit as st

from dashboard.figures import duration_figure, variance_figure
from dashboard.theme import lesson_banner, next_lesson, show
from montecarlo.project import (
    DEFAULT_DEADLINE,
    DEFAULT_TASKS,
    Task,
    explain_deadline,
    fastest_total,
    interpret_deadline,
    simulate_project,
    slowest_total,
    task_variance_formula,
)


@st.cache_data(show_spinner=False)
def _load_project(lows, modes, highs, n: int, seed: int, shared_slip: float):
    tasks = tuple(
        Task(template.name, low, mode, high)
        for template, low, mode, high in zip(DEFAULT_TASKS, lows, modes, highs)
    )
    return tasks, simulate_project(tasks, n=n, seed=seed, shared_slip=shared_slip)


def _seed() -> int:
    if "project_seed" not in st.session_state:
        st.session_state.project_seed = 11
    if st.button("New projects", type="primary", key="new_projects"):
        st.session_state.project_seed += 1
    return int(st.session_state.project_seed)


def page() -> None:
    st.header("A deadline you can miss")
    lesson_banner(
        "Adding the most-likely durations gives one total. "
        "Simulating the ranges you already believe gives the chance of meeting a deadline."
    )
    st.markdown(
        """
Three tasks run in sequence. For each one you set a lowest duration, a most
likely duration, and a highest duration, in working days. The triangular
distribution puts the most probability on the most likely value and tapers in
straight lines to the ends.

The mean of a sum is the sum of the means, so the average duration is arithmetic,
not a simulation. The probability of finishing by a deadline has no short formula
for three different triangles. Drawing the sum many times estimates it. A "hit"
on the dartboard was "inside the quarter disk". A hit here is "total at or under
the deadline". Both hits are averaged.

π had an area formula, which is what let the earlier lessons check the method.
Here the sample is the answer you keep.
        """
    )

    edited: list[tuple[float, float, float]] = []
    for template in DEFAULT_TASKS:
        st.markdown(f"**{template.name}**")
        low_col, mode_col, high_col = st.columns(3)
        with low_col:
            low = st.number_input("Lowest", min_value=0.0, max_value=80.0, value=float(template.low), step=0.5, key=f"{template.name}_low")
        with mode_col:
            mode = st.number_input("Most likely", min_value=0.0, max_value=80.0, value=float(template.mode), step=0.5, key=f"{template.name}_mode")
        with high_col:
            high = st.number_input("Highest", min_value=0.0, max_value=80.0, value=float(template.high), step=0.5, key=f"{template.name}_high")
        edited.append((float(low), float(mode), float(high)))

    try:
        tasks = tuple(Task(template.name, low, mode, high) for template, (low, mode, high) in zip(DEFAULT_TASKS, edited))
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    st.subheader("Modes and means, before any random draws")
    st.dataframe(_moment_table(tasks), hide_index=True, width="stretch")
    st.caption(
        "Mean = (lowest + most likely + highest) / 3. "
        "When the pessimistic side is longer than the optimistic side, the mean sits above the most likely value. "
        f"The most-likely plan totals {sum(task.mode for task in tasks):g} days. "
        f"The mean plan totals {sum(task.mean for task in tasks):.2f} days."
    )

    controls = st.columns((1.1, 1.1, 1.2, 0.7))
    with controls[0]:
        n = st.slider("Simulated projects", min_value=2_000, max_value=50_000, value=20_000, step=2_000)
    with controls[1]:
        shared = st.slider(
            "Shared slip, up to (days)",
            min_value=0.0,
            max_value=10.0,
            value=0.0,
            step=0.5,
            help="One extra delay, drawn uniformly from 0 to this value, added to every simulated project. Zero means the tasks are independent.",
        )
    with controls[2]:
        deadline = st.slider("Deadline (working days)", min_value=0.0, max_value=80.0, value=DEFAULT_DEADLINE, step=0.5)
    with controls[3]:
        seed = _seed()
        st.caption(f"Seed {seed}")

    # The cache key is the numeric bounds. Names stay the three defaults.
    _, result = _load_project(
        tuple(task.low for task in tasks),
        tuple(task.mode for task in tasks),
        tuple(task.high for task in tasks),
        n,
        seed,
        shared,
    )
    probability = result.probability_on_time(deadline)

    metrics = st.columns(4)
    metrics[0].metric("On time", _shown_probability(probability))
    metrics[1].metric("Sample mean", f"{result.mean:.1f} d")
    metrics[2].metric("80th percentile", f"{result.percentiles[80]:.1f} d")
    metrics[3].metric("Most-likely total", f"{result.sum_of_modes:.0f} d")
    st.caption(
        f"Formula for the mean, including half the shared slip: {result.formula_mean:.2f} days. "
        f"Sample mean of these {result.n:,} projects: {result.mean:.2f} days. "
        "The two agree up to ordinary sampling noise, which is a check that the draws follow the distributions you specified."
    )
    st.markdown(interpret_deadline(tasks, result, deadline))

    if np_range_collapsed(result.totals):
        st.info("Every simulated total landed on the same value.")
    else:
        show(
            duration_figure(
                result.totals,
                deadline,
                result.sum_of_modes,
                result.percentiles[80],
            )
        )
        st.caption(
            f"Fastest combination in the model: {fastest_total(tasks):.1f} days. "
            f"Slowest: {slowest_total(tasks, shared):.1f} days. "
            "Teal bars finish by the deadline. Orange bars miss it. "
            "Drag the deadline across the histogram; the sample of projects stays fixed, and only the question changes."
        )

    st.subheader("Where the uncertainty sits")
    show(variance_figure(result.variance_share))
    st.caption(
        "Under independence, the variance of a sum is the sum of the variances. "
        "The shares use the theoretical variance of each distribution, so they do not jitter when you redraw. "
        "The task with the long pessimistic tail usually dominates the total."
    )
    st.subheader("The arithmetic")
    st.code(explain_deadline(result, deadline), language="text")
    st.caption("Same pattern as the darts: count the hits, divide by n.")

    st.subheader("Eight simulated projects")
    st.dataframe(_preview_table(result.preview, deadline), hide_index=True, width="stretch")
    st.caption("Each row adds one draw from each task, plus the shared delay. The total is what the histogram is counting.")

    with st.expander("Variance formula, with these numbers"):
        for task in tasks:
            st.code(task_variance_formula(task), language="text")
        if shared > 0:
            st.code(
                f"Shared slip: variance of Uniform(0, {shared:g}) = {shared:g}² / 12 = {shared**2 / 12:.3f}",
                language="text",
            )

    next_lesson("What to take with you")


def _moment_table(tasks: tuple[Task, ...]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for task in tasks:
        rows.append(
            {
                "Task": task.name,
                "Lowest": _num(task.low),
                "Most likely": _num(task.mode),
                "Highest": _num(task.high),
                "Mean": round(task.mean, 2),
            }
        )
    rows.append(
        {
            "Task": "Total",
            "Lowest": _num(sum(task.low for task in tasks)),
            "Most likely": _num(sum(task.mode for task in tasks)),
            "Highest": _num(sum(task.high for task in tasks)),
            "Mean": round(sum(task.mean for task in tasks), 2),
        }
    )
    return rows


def _preview_table(preview, deadline: float) -> list[dict[str, object]]:
    rows = []
    for row in preview:
        display: dict[str, object] = {}
        for key, value in row.items():
            display[key] = round(value, 2)
        display["On time"] = "yes" if row["Total"] <= deadline else "no"
        rows.append(display)
    return rows


def _shown_probability(probability: float) -> str:
    if probability <= 0:
        return "0%"
    if probability >= 1:
        return "100%"
    return f"{probability:.1%}"


def _num(value: float) -> int | float:
    rounded = round(value, 2)
    if float(rounded).is_integer():
        return int(rounded)
    return rounded


def np_range_collapsed(totals) -> bool:
    return bool(totals.min() == totals.max())
