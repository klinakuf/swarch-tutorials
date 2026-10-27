"""A small Monte Carlo tutorial library.

Read ``pi.py`` first. It estimates π with uniform darts and is the whole
method in one screen of code. ``project.py`` applies the same average to a
deadline. ``convergence.py`` repeats the π experiment so the 1/√n law and
the meaning of a 95% interval can be checked.
"""

from montecarlo.convergence import (
    CoverageResult,
    ConvergenceResult,
    convergence_grid,
    interval_coverage,
)
from montecarlo.pi import (
    ERROR_CONSTANT,
    TRUE_HIT_PROBABILITY,
    PiResult,
    confidence_interval,
    critical_value,
    estimate_pi,
    explain_estimate,
    pointwise_band,
    running_estimate,
    samples_needed,
)
from montecarlo.project import (
    DEFAULT_DEADLINE,
    DEFAULT_TASKS,
    ProjectResult,
    Task,
    explain_deadline,
    fastest_total,
    interpret_deadline,
    sample_triangular,
    simulate_project,
    slowest_total,
)

__all__ = [
    "CoverageResult",
    "ConvergenceResult",
    "DEFAULT_DEADLINE",
    "DEFAULT_TASKS",
    "ERROR_CONSTANT",
    "PiResult",
    "ProjectResult",
    "TRUE_HIT_PROBABILITY",
    "Task",
    "confidence_interval",
    "convergence_grid",
    "critical_value",
    "estimate_pi",
    "explain_deadline",
    "explain_estimate",
    "fastest_total",
    "interpret_deadline",
    "interval_coverage",
    "pointwise_band",
    "running_estimate",
    "sample_triangular",
    "samples_needed",
    "simulate_project",
    "slowest_total",
]
