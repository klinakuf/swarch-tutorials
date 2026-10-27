"""Lesson 1: the model, the estimator, and the size of the error."""

from __future__ import annotations

import streamlit as st

from dashboard.figures import theory_figure
from dashboard.theme import lesson_banner, next_lesson, show
from montecarlo.pi import estimate_pi


def page() -> None:
    st.header("The idea")
    lesson_banner(
        "Monte Carlo estimates a number by turning it into an average, "
        "then simulating that average many times."
    )

    picture, words = st.columns((1.05, 0.95), gap="large")
    with picture:
        sample = estimate_pi(24, seed=4)
        show(theory_figure(sample.x, sample.y, sample.inside))
        st.caption("Twenty-four uniform darts. Teal landed in the quarter disk; orange landed in the rest of the square.")
    with words:
        st.subheader("A number, written as a probability")
        st.markdown(
            """
The unit square is every point $(x, y)$ with both coordinates between 0 and 1.
Its area is 1.

The quarter disk of radius 1, centered at the origin, has area $\\pi/4$.
A dart thrown uniformly at the square lands in that quarter disk with probability
equal to the ratio of the areas.
            """
        )
        st.latex(r"P(X^{2}+Y^{2}\le 1)=\frac{\pi}{4}")
        st.markdown("Rearrange, and π is four times a probability.")
        st.latex(r"\pi = 4\,P(X^{2}+Y^{2}\le 1)")

    st.subheader("The computation")
    st.markdown(
        """
Draw $x$ and $y$ independently from Uniform(0, 1). Count a hit when
$x^{2}+y^{2}\\le 1$. Repeat $n$ times. The fraction of hits estimates the
probability, and four times that fraction estimates π.
        """
    )
    st.latex(
        r"\hat\pi_n = 4 \cdot \frac{1}{n}\sum_{i=1}^{n} \mathbf{1}(X_i^{2}+Y_i^{2}\le 1)"
    )
    st.markdown(
        """
That is a sample mean. The deadline lesson later in the sidebar is the same
line of code aimed at a different yes/no question: "did this simulated project
finish on time?" NumPy draws the points. The multiplication and the counting
are the estimator.
        """
    )

    st.subheader("How large the error is")
    st.markdown(
        """
One throw is a yes/no outcome with success probability $p=\\pi/4$.
A yes/no outcome has variance $p(1-p)$. The average of $n$ independent throws
has variance $p(1-p)/n$, so its standard deviation is the square root of that.
Multiplying by 4, to get from a probability to π, multiplies the standard
deviation by 4.
        """
    )
    st.latex(r"\mathrm{SE}(\hat\pi_n)=4\sqrt{\frac{p(1-p)}{n}}=\frac{C}{\sqrt{n}}")
    st.markdown(
        """
Three consequences follow, and the next two lessons draw them.

**The average settles.** As $n$ grows, the standard error goes to 0, so
$\\hat\\pi_n$ settles on π. This is the law of large numbers. The estimator
is exactly unbiased at every $n$: its expected value is π. A single run still
misses, by about one standard error. Unbiased describes the average of many
runs. It does not describe the run in front of you.

**The shrinkage is slow.** The denominator is $\\sqrt{n}$. Quadrupling the
throws halves the typical error. A tenfold tighter answer takes about a
hundredfold more throws.

**A 95% interval is a claim about the procedure.** For large $n$ the error is
approximately normal, which is the central limit theorem in the form used here.
SciPy's normal quantile gives $z\\approx 1.96$ for 95%. The random interval
$\\hat\\pi \\pm z\\times\\mathrm{SE}$ covers the fixed number π in about 95 of
100 repeated experiments. In practice $p$ is unknown, and the fraction of hits
stands in for it.
        """
    )

    st.subheader("What the other lessons make visible")
    st.markdown(
        """
- **Throwing darts at π.** One experiment, the arithmetic with the numbers filled in, and a path that starts at 0 or 4 and settles.
- **The slow square root.** Hundreds of experiments side by side, and a check of whether the 95% intervals earn that name.
- **A deadline you can miss.** Three uncertain tasks. Adding the most-likely durations and simulating the ranges answer different questions.
- **What to take with you.** What the percentage is counting, and what a target precision costs.
        """
    )
    next_lesson("Throwing darts at π")
