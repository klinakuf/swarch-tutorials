"""A three-task project, and the chance it finishes by a deadline.

Each task has a triangular duration: a lowest plausible value, a most likely
value, and a highest plausible value. Probability is highest at the most
likely value and falls in straight lines to the two ends. Tasks run in
sequence, so the project duration is the sum.

The mean of a sum is the sum of the means, so the average duration needs no
simulation. The probability of meeting a deadline does. The sum of three
different triangular distributions has a cumbersome formula; drawing the sum
many times estimates that probability directly.

The default numbers are chosen so that a plan made by adding the most-likely
durations looks comfortable against the deadline, while the mean of the sum
is already past it. Skew does that. The long pessimistic side of a triangle
pulls the mean above the most likely value:

    mean = (lowest + most likely + highest) / 3.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from scipy import stats

DEFAULT_DEADLINE = 18.0


@dataclass(frozen=True)
class Task:
    """A triangular duration, in working days."""

    name: str
    low: float
    mode: float
    high: float

    def __post_init__(self) -> None:
        if self.high <= self.low or not (self.low <= self.mode <= self.high):
            raise ValueError(
                f"{self.name}: enter a lowest value, a most likely value between "
                f"the ends, and a highest value above the lowest. "
                f"Received {self.low:g}, {self.mode:g}, {self.high:g}."
            )

    @property
    def mean(self) -> float:
        """Mean of a triangular distribution. The most likely value is a different number when the triangle is skewed."""
        return (self.low + self.mode + self.high) / 3.0

    @property
    def variance(self) -> float:
        """Variance of a triangular distribution. Matches ``scipy.stats.triang``."""
        a, b, c = self.low, self.mode, self.high
        return (a * a + b * b + c * c - a * b - a * c - b * c) / 18.0


DEFAULT_TASKS: tuple[Task, ...] = (
    Task("Design", 2.0, 4.0, 7.0),
    Task("Build", 6.0, 9.0, 18.0),
    Task("Test", 2.0, 3.0, 10.0),
)


@dataclass(frozen=True)
class ProjectResult:
    """One Monte Carlo sample of total project duration."""

    totals: np.ndarray
    n: int
    seed: int
    shared_slip: float
    mean: float
    sum_of_modes: float
    sum_of_means: float
    formula_mean: float
    percentiles: dict[int, float]
    variance_share: dict[str, float]
    preview: tuple[dict[str, float], ...]

    def probability_on_time(self, deadline: float) -> float:
        """Fraction of simulated projects with total ≤ deadline."""
        return float(np.mean(self.totals <= deadline))


def sample_triangular(
    rng: np.random.Generator,
    low: float,
    mode: float,
    high: float,
    n: int,
) -> np.ndarray:
    """Draw n triangular durations specified as lowest, most likely, highest.

    SciPy parameterizes the same distribution with a shape ``c`` in [0, 1],
    a location at the low end, and a scale equal to the width::

        c = (mode − low) / (high − low)
        mode = loc + c × scale
    """
    width = high - low
    shape = (mode - low) / width
    return stats.triang.rvs(shape, loc=low, scale=width, size=n, random_state=rng)


def _streams(seed: int, count: int) -> list[np.random.Generator]:
    """Independent generators spawned from one seed.

    Separate streams keep the task draws stable when the shared-slip stream
    is or is not consumed. Turning the shared delay on adds a common shock
    to the same tasks.
    """
    parent = np.random.SeedSequence(seed)
    return [np.random.default_rng(child) for child in parent.spawn(count)]


def simulate_project(
    tasks: Sequence[Task],
    n: int,
    seed: int,
    shared_slip: float = 0.0,
) -> ProjectResult:
    """Simulate ``n`` independent projects and summarize the total duration.

    Parameters
    ----------
    tasks:
        Sequential tasks. The total is the sum of one draw from each.
    n:
        Number of simulated projects.
    seed:
        Reproducible seed. Task draws depend on the seed and the task list,
        and stay fixed when ``shared_slip`` changes.
    shared_slip:
        Upper end of an extra delay, drawn once per project from Uniform(0, S)
        and added to the total. Zero leaves the tasks independent. This is
        the simplest common-cause shock: one event that moves the whole project.
    """
    if n < 1:
        raise ValueError("n must be at least 1")
    if shared_slip < 0:
        raise ValueError("shared_slip must be ≥ 0")
    if len(tasks) == 0:
        raise ValueError("provide at least one task")

    validated = tuple(Task(t.name, float(t.low), float(t.mode), float(t.high)) for t in tasks)
    names = [t.name for t in validated]
    if len(set(names)) != len(names):
        raise ValueError("task names must be unique")

    streams = _streams(seed, len(validated) + 1)
    draws: dict[str, np.ndarray] = {}
    for task, stream in zip(validated, streams):
        draws[task.name] = sample_triangular(stream, task.low, task.mode, task.high, n)

    if shared_slip > 0:
        shared = streams[-1].uniform(0.0, shared_slip, size=n)
    else:
        shared = np.zeros(n, dtype=np.float64)

    totals = shared.copy()
    for name in names:
        totals = totals + draws[name]

    variances = {task.name: task.variance for task in validated}
    if shared_slip > 0:
        variances["Shared slip"] = shared_slip**2 / 12.0
    variance_total = sum(variances.values())
    variance_share = {name: value / variance_total for name, value in variances.items()}

    query = (10, 50, 80, 90)
    percentiles = {q: float(np.quantile(totals, q / 100.0)) for q in query}

    preview_n = min(8, n)
    preview: list[dict[str, float]] = []
    for i in range(preview_n):
        row = {name: float(draws[name][i]) for name in names}
        row["Shared slip"] = float(shared[i])
        row["Total"] = float(totals[i])
        preview.append(row)

    sum_of_means = sum(task.mean for task in validated)
    return ProjectResult(
        totals=totals,
        n=n,
        seed=int(seed),
        shared_slip=float(shared_slip),
        mean=float(totals.mean()),
        sum_of_modes=float(sum(task.mode for task in validated)),
        sum_of_means=float(sum_of_means),
        formula_mean=float(sum_of_means + shared_slip / 2.0),
        percentiles=percentiles,
        variance_share=variance_share,
        preview=tuple(preview),
    )


def fastest_total(tasks: Sequence[Task], shared_slip: float = 0.0) -> float:
    """Shortest total the ranges can produce. The shared delay can be zero."""
    del shared_slip  # The shared delay is at least 0, so it does not raise the floor.
    return float(sum(task.low for task in tasks))


def slowest_total(tasks: Sequence[Task], shared_slip: float = 0.0) -> float:
    """Longest total the ranges can produce, including the largest shared delay."""
    return float(sum(task.high for task in tasks) + shared_slip)


def explain_deadline(result: ProjectResult, deadline: float) -> str:
    """The arithmetic of the on-time probability, with the current numbers filled in."""
    on_time = int(np.sum(result.totals <= deadline))
    probability = on_time / result.n
    return "\n".join(
        [
            f"n        = {result.n:,}",
            f"on_time  = count(total <= {deadline:g}) = {on_time:,}",
            f"P_hat    = on_time / n = {probability:.4f}",
            f"mean     = average(total) = {result.mean:.3f}",
            f"formula  = sum of task means + shared/2 = {result.formula_mean:.3f}",
            f"p80      = {result.percentiles[80]:.3f}",
        ]
    )


def _percent(probability: float) -> str:
    if probability <= 0:
        return "0%"
    if probability >= 1:
        return "100%"
    return f"{probability:.1%}"


def interpret_deadline(
    tasks: Sequence[Task],
    result: ProjectResult,
    deadline: float,
) -> str:
    """A short reading of the current sample, in days and probabilities."""
    probability = result.probability_on_time(deadline)
    fastest = fastest_total(tasks, result.shared_slip)
    slowest = slowest_total(tasks, result.shared_slip)
    sentences: list[str] = []

    if deadline < fastest:
        sentences.append(
            f"The deadline of {deadline:g} days is earlier than the fastest combination "
            f"in the ranges, {fastest:g} days. Every simulated project misses."
        )
    elif deadline >= slowest:
        sentences.append(
            f"The deadline of {deadline:g} days is at or after the slowest combination "
            f"in the ranges, {slowest:g} days. Every simulated project finishes on time."
        )
    else:
        sentences.append(
            f"{_percent(probability)} of simulated projects finish by day {deadline:g}. "
            f"Adding the most-likely durations gives {result.sum_of_modes:g} days. "
            f"The mean duration is {result.formula_mean:.1f} days."
        )
        if result.sum_of_modes <= deadline < result.formula_mean:
            sentences.append(
                "The deadline clears that most-likely total and still sits short of the mean. "
                "Each skewed range is pulled toward its longer side, and those pulls add up."
            )
        sentences.append(
            f"The 80th percentile is {result.percentiles[80]:.1f} days: "
            f"about 80% of simulated projects finish by then."
        )

    if result.shared_slip > 0:
        sentences.append(
            f"Every total also includes one shared delay drawn from 0 to "
            f"{result.shared_slip:g} days, whose mean is {result.shared_slip / 2:g} days."
        )

    sentences.append(
        "This percentage counts draws from the ranges you entered. Move a range, and the percentage moves with it."
    )
    return " ".join(sentences)


def task_variance_formula(task: Task) -> str:
    """One task's variance, with its numbers substituted into the formula."""
    a, b, c = task.low, task.mode, task.high
    return (
        f"{task.name}: (low² + mode² + high² − low·mode − low·high − mode·high) / 18 "
        f"= ({a:g}² + {b:g}² + {c:g}² − {a:g}·{b:g} − {a:g}·{c:g} − {b:g}·{c:g}) / 18 "
        f"= {task.variance:.3f}"
    )
