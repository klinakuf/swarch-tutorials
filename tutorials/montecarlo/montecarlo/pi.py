"""Estimate π by throwing darts at the unit square.

The model is small enough to draw. The unit square has area 1. The quarter
disk of radius 1 inside it has area π/4. A point thrown uniformly at random
therefore lands inside the quarter disk with probability π/4, which means

    π = 4 × P(X² + Y² ≤ 1).

Monte Carlo replaces the probability with the fraction of hits in a sample.
The same pattern — turn a question into an average, then simulate the average —
is the whole method. ``montecarlo.project`` uses it on a deadline.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.stats import norm

# P(a uniform point in the unit square lands in the quarter disk).
TRUE_HIT_PROBABILITY = math.pi / 4

# Standard error of the π estimator is ERROR_CONSTANT / sqrt(n).
ERROR_CONSTANT = 4.0 * math.sqrt(TRUE_HIT_PROBABILITY * (1.0 - TRUE_HIT_PROBABILITY))


@dataclass(frozen=True)
class PiResult:
    """One experiment of ``n`` independent throws."""

    x: np.ndarray
    y: np.ndarray
    inside: np.ndarray
    n: int
    seed: int

    def prefix(self, k: int) -> PiResult:
        """The same throws, counting only the first ``k``."""
        if not 1 <= k <= self.n:
            raise ValueError(f"k must be between 1 and {self.n}")
        return PiResult(
            x=self.x[:k],
            y=self.y[:k],
            inside=self.inside[:k],
            n=k,
            seed=self.seed,
        )

    @property
    def hits(self) -> int:
        return int(self.inside.sum())

    @property
    def hit_probability(self) -> float:
        return self.hits / self.n

    @property
    def estimate(self) -> float:
        """π̂ = 4 × (hits / n)."""
        return 4.0 * self.hit_probability

    @property
    def standard_error(self) -> float:
        """Estimated standard deviation of π̂, computed from the sample alone.

        One throw is a yes/no trial with unknown success probability p.
        The variance of a yes/no trial is p(1 − p). The average of n
        independent throws has variance p(1 − p) / n. Multiplying that
        average by 4, to turn a probability into an estimate of π,
        multiplies the standard deviation by 4.

        The sample fraction stands in for the unknown p.
        """
        p = self.hit_probability
        return 4.0 * math.sqrt(p * (1.0 - p) / self.n)

    @property
    def true_standard_error(self) -> float:
        """Standard deviation of π̂ using the known value p = π/4.

        A real problem does not hand you this number: it depends on the
        answer under estimation. It is the right yardstick when the goal
        is to check the method against a known π.
        """
        return ERROR_CONSTANT / math.sqrt(self.n)


def estimate_pi(n: int, seed: int) -> PiResult:
    """Throw ``n`` darts at the unit square and estimate π.

    Parameters
    ----------
    n:
        Number of independent points. The typical error shrinks like
        1/√n. Cutting the error by 10 takes about 100 times as many throws.
    seed:
        Seed for NumPy's Generator, so a figure can be drawn again exactly.
    """
    if n < 1:
        raise ValueError("n must be at least 1")

    rng = np.random.default_rng(seed)
    x = rng.random(n)
    y = rng.random(n)
    inside = x * x + y * y <= 1.0
    return PiResult(x=x, y=y, inside=inside, n=n, seed=int(seed))


def running_estimate(inside: np.ndarray) -> np.ndarray:
    """π̂ after 1 throw, after 2 throws, …, after n throws, in order."""
    counts = np.cumsum(inside, dtype=np.float64)
    throws = np.arange(1, inside.size + 1, dtype=np.float64)
    return 4.0 * counts / throws


def critical_value(level: float = 0.95) -> float:
    """Normal quantile z with P(−z < Z < z) = ``level``.

    SciPy computes it. For 95% the value is about 1.96.
    """
    if not 0.0 < level < 1.0:
        raise ValueError("level must be strictly between 0 and 1")
    return float(norm.ppf(0.5 + level / 2.0))


def confidence_interval(
    estimate: float,
    standard_error: float,
    level: float = 0.95,
) -> tuple[float, float]:
    """Normal interval: estimate ± z × standard error."""
    z = critical_value(level)
    half = z * standard_error
    return estimate - half, estimate + half


def pointwise_band(n: int, level: float = 0.95) -> tuple[np.ndarray, np.ndarray]:
    """π ± z × (true standard error) at every sample size from 1 to n.

    Read the band at a fixed n: about ``level`` of repeated experiments
    land inside it at that n. A running path is a sequence of sample sizes,
    and an ordinary path steps outside the band along the way. The band is
    a statement about experiments at one n, not a tube the path must stay in.
    """
    if n < 1:
        raise ValueError("n must be at least 1")
    z = critical_value(level)
    counts = np.arange(1, n + 1, dtype=np.float64)
    half = z * ERROR_CONSTANT / np.sqrt(counts)
    return math.pi - half, math.pi + half


def samples_needed(margin: float, level: float = 0.95) -> int:
    """Smallest n whose theoretical interval half-width is at most ``margin``.

    Solves z × C / √n ≤ margin, with C = 4 √[p(1 − p)] and p = π/4.
    The formula uses the true hit probability, so it is a sample-size plan
    for this dartboard. In a problem where p is unknown, a guess for p
    takes its place.
    """
    if margin <= 0:
        raise ValueError("margin must be positive")
    z = critical_value(level)
    n = (z * ERROR_CONSTANT / margin) ** 2
    return int(math.ceil(n - 1e-9))


def explain_estimate(result: PiResult, level: float = 0.95) -> str:
    """The arithmetic of one experiment, with the current numbers filled in."""
    p = result.hit_probability
    z = critical_value(level)
    se = result.standard_error
    low, high = confidence_interval(result.estimate, se, level)
    return "\n".join(
        [
            f"n        = {result.n:,}",
            f"hits     = {result.hits:,}",
            f"p_hat    = hits / n = {p:.6f}",
            f"pi_hat   = 4 * p_hat = {result.estimate:.6f}",
            f"SE       = 4 * sqrt(p_hat * (1 - p_hat) / n) = {se:.6f}",
            f"z        = {z:.4f}   (SciPy normal quantile for {level:.0%})",
            f"interval = pi_hat ± z * SE = [{low:.4f}, {high:.4f}]",
        ]
    )
