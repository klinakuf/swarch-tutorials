"""Lesson 5: what the percentage means, and what a precision target costs."""

from __future__ import annotations

import streamlit as st

from dashboard.theme import lesson_banner
from montecarlo.pi import ERROR_CONSTANT, TRUE_HIT_PROBABILITY, critical_value, samples_needed


def page() -> None:
    st.header("What to take with you")
    lesson_banner(
        "A Monte Carlo percentage is a count of draws from a model, "
        "and its precision is bought with the square root of the number of draws."
    )

    st.subheader("What a given precision costs")
    st.markdown(
        """
On the dartboard the standard error is $C/\\sqrt{n}$, so the number of throws
needed for a 95% half-width of $\\varepsilon$ is the formula below, solved for $n$.
The constant uses the true hit probability $p=\\pi/4$. It is a sample-size plan
for this dartboard. A different question has a different constant in place of $C$.
        """
    )
    margin = st.slider("Target half-width on π", min_value=0.001, max_value=0.05, value=0.01, step=0.001, format="%.3f")
    needed = samples_needed(margin)
    tighter = samples_needed(margin / 10)
    st.metric(f"Throws for a 95% half-width of ±{margin:.3f}", f"{needed:,}")
    st.code(
        "\n".join(
            [
                f"p = π/4 = {TRUE_HIT_PROBABILITY:.6f}",
                f"z = {critical_value():.4f}",
                f"C = 4 * sqrt(p * (1 - p)) = {ERROR_CONSTANT:.4f}",
                f"n = ceil((z * C / {margin:.3f})²) = {needed:,}",
            ]
        ),
        language="text",
    )
    st.markdown(
        f"A band ten times tighter, ±{margin / 10:.4f}, needs **{tighter:,}** throws, "
        f"which is {tighter / needed:.0f}× more. The factor is about 100 because the "
        f"error depends on $\\sqrt{{n}}$, and $10^{2} = 100$."
    )

    st.subheader("The interval describes the procedure")
    st.markdown(
        """
Build the interval as estimate ± 1.96 × standard error, and repeat the whole
experiment. About 95 of 100 intervals contain the true number, once $n$ is
large enough for the normal approximation. The chart of teal and orange
segments on "The slow square root" is that count. The interval in your hand
is one draw from the procedure. The procedure's success rate is a fact about
the method. It does not label your one interval as a success or a miss.
        """
    )

    st.subheader("Precision scales with the square root")
    st.markdown(
        """
Quadrupling the draws halves the typical error. The calculator above is that
relation solved for the number of draws, and the log-log chart is the same
relation measured on repeated dartboard experiments. Budget the runs from the
square root, with the constant that belongs to the quantity you care about.
        """
    )

    st.subheader("The percentage counts draws from the model you typed in")
    st.markdown(
        """
The on-time figure is the fraction of projects whose durations came from the
lowest, most likely, and highest values on the previous page. Change a
pessimistic end, and the fraction changes with it. The simulation adds and
counts. The ranges are the assumptions, carried through as written. When a
known answer exists, as π does, the sample can be checked against it. When
the deadline probability is the unknown, the sample is only as trustworthy
as those ranges.
        """
    )

    st.subheader("A shared delay thickens the late tail")
    st.markdown(
        """
The default project adds independent task draws. A blocked review, an illness,
or a late dependency is one cause with one duration, felt by the whole project.
The shared-slip slider puts one Uniform delay on every simulated total. The
on-time probability drops while each task's own range stays fixed. A model that
omits a common cause answers a question in which that cause is absent.
        """
    )

    st.subheader("Read a planning date from the distribution of the total")
    st.markdown(
        """
The sum of most-likely durations sits on the short side of a skewed range,
because a triangular mean is (lowest + most likely + highest) / 3 and the long
side pulls that average up. On the default numbers the most-likely total is
16 days, the mean is about 20.3, and a deadline of 18 clears the first number
and misses the second. The 80th percentile of the simulated totals is a single
date that already includes that skew. It is a planning number read off the
histogram, earned by the shape of the ranges.
        """
    )

    st.subheader("Rare outcomes need a great many trials")
    st.markdown(
        """
An event with probability 0.001 appears about once per thousand trials. A run
of a thousand such trials often records a count of zero, and the estimated
probability is then 0. Estimating a rare event means choosing a number of
trials large compared with $1/p$, and then paying the usual $\\sqrt{n}$ cost
on top if the estimate needs to be precise.
        """
    )

    st.subheader("Where the method grows up")
    st.markdown(
        """
This tutorial uses independent draws, which is the case the plain $\\sqrt{n}$
formula describes.

- **Variance reduction.** Antithetic pairs and control variates keep the same
  estimator and shrink the constant $C$ in $C/\\sqrt{n}$.
- **Quasi-Monte Carlo.** Low-discrepancy sequences replace pure randomness and,
  on smooth low-dimensional problems, can converge faster than $1/\\sqrt{n}$.
- **Markov chain Monte Carlo.** Used when a point can be scored but an
  independent sample is hard to draw. Standard errors for dependent draws are
  a further topic.
- **Richer simulations.** Queues, inventories, and geometric Brownian motion
  are the same pattern: simulate one path, summarize it, repeat. The π
  estimator is that pattern with the path reduced to a single yes or no.
        """
    )
