"""Many repetitions of the π experiment, to see the sampling distribution.

One run of ``estimate_pi`` produces one number, π̂. That number is random.
The way to see its randomness is to run the whole experiment many times and
keep every estimate. The spread of those estimates is what the standard-error
formula predicts, and it shrinks like 1/√n.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from montecarlo.pi import ERROR_CONSTANT, critical_value


@dataclass(frozen=True)
class ConvergenceResult:
    """Estimates of π on a grid of sample sizes.

    ``estimates[i, j]`` is the result of replication ``j`` at ``sample_sizes[i]``.
    """

    sample_sizes: np.ndarray
    estimates: np.ndarray
    theoretical_se: np.ndarray
    empirical_sd: np.ndarray
    rmse: np.ndarray

    @property
    def error_times_sqrt_n(self) -> np.ndarray:
        """RMSE × √n. The square-root law says this column stays near ``ERROR_CONSTANT``."""
        return self.rmse * np.sqrt(self.sample_sizes.astype(np.float64))


def convergence_grid(
    sample_sizes: list[int] | tuple[int, ...],
    replications: int,
    seed: int,
) -> ConvergenceResult:
    """Repeat the dartboard experiment at each sample size.

    Each replication draws its own points. The theoretical standard error at
    size n is C / √n, with C = 4 √[p(1 − p)] and p = π/4. The empirical
    RMSE is the square root of the average squared distance from π across
    replications. For this unbiased estimator the two describe the same spread.
    """
    if replications < 2:
        raise ValueError("replications must be at least 2")
    sizes = [int(n) for n in sample_sizes]
    if not sizes or any(n < 1 for n in sizes):
        raise ValueError("sample sizes must be positive")

    rng = np.random.default_rng(seed)
    estimates = np.empty((len(sizes), replications), dtype=np.float64)
    for i, n in enumerate(sizes):
        x = rng.random((replications, n))
        y = rng.random((replications, n))
        hits = np.count_nonzero(x * x + y * y <= 1.0, axis=1)
        estimates[i] = 4.0 * hits / n

    size_array = np.asarray(sizes, dtype=np.int64)
    theoretical = ERROR_CONSTANT / np.sqrt(size_array.astype(np.float64))
    empirical_sd = estimates.std(axis=1, ddof=1)
    rmse = np.sqrt(np.mean((estimates - math.pi) ** 2, axis=1))
    return ConvergenceResult(
        sample_sizes=size_array,
        estimates=estimates,
        theoretical_se=theoretical,
        empirical_sd=empirical_sd,
        rmse=rmse,
    )


@dataclass(frozen=True)
class CoverageResult:
    """Normal intervals from repeated experiments, and whether each one covers π."""

    n: int
    level: float
    estimates: np.ndarray
    low: np.ndarray
    high: np.ndarray
    covered: np.ndarray

    @property
    def coverage(self) -> float:
        return float(np.mean(self.covered))

    @property
    def replications(self) -> int:
        return int(self.covered.size)

    @property
    def degenerate(self) -> int:
        """Intervals whose sample standard error was zero.

        That happens when every dart in an experiment lands on the same side
        of the arc. The interval then collapses to a point, and the normal
        recipe has failed because the sample was too small to show any variation.
        """
        return int(np.sum((self.high - self.low) <= 1e-12))


def interval_coverage(
    n: int,
    replications: int,
    seed: int,
    level: float = 0.95,
) -> CoverageResult:
    """Build a normal  interval for each of ``replications`` experiments.

    The interval uses the sample standard error, which is the interval you
    can report when π is unknown. ``coverage`` is the fraction that contained
    the true π. For large n that fraction sits near ``level``.
    """
    if n < 1:
        raise ValueError("n must be at least 1")
    if replications < 1:
        raise ValueError("replications must be at least 1")

    rng = np.random.default_rng(seed)
    x = rng.random((replications, n))
    y = rng.random((replications, n))
    p_hat = np.mean(x * x + y * y <= 1.0, axis=1)
    estimates = 4.0 * p_hat
    standard_error = 4.0 * np.sqrt(p_hat * (1.0 - p_hat) / n)
    z = critical_value(level)
    low = estimates - z * standard_error
    high = estimates + z * standard_error
    covered = (low <= math.pi) & (math.pi <= high)
    return CoverageResult(
        n=n,
        level=level,
        estimates=estimates,
        low=low,
        high=high,
        covered=covered,
    )
