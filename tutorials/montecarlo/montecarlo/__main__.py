"""Print a short numeric sketch of both models.

The dashboard (``streamlit run app.py`` from this tutorial folder) is the
tutorial. This module is the same arithmetic without the pictures, so you can
see the numbers in a terminal.
"""

from __future__ import annotations

import math

from montecarlo.pi import estimate_pi, explain_estimate, samples_needed
from montecarlo.project import DEFAULT_DEADLINE, DEFAULT_TASKS, explain_deadline, simulate_project


def main() -> None:
    pi = estimate_pi(10_000, seed=7)
    project = simulate_project(DEFAULT_TASKS, n=20_000, seed=11, shared_slip=0.0)
    needed = samples_needed(0.01)

    print("Monte Carlo, from one picture")
    print("=" * 32)
    print()
    print("Darts on the unit square")
    print(explain_estimate(pi))
    print(f"true pi  = {math.pi:.6f}")
    print(f"throws for a 95% half-width of 0.01: {needed:,}")
    print()
    print(f"Three tasks, deadline {DEFAULT_DEADLINE:g} working days")
    print(explain_deadline(project, DEFAULT_DEADLINE))
    print(f"sum of most-likely durations = {project.sum_of_modes:g}")
    print()
    print("Dashboard: cd tutorials/montecarlo && streamlit run app.py")


if __name__ == "__main__":
    main()
