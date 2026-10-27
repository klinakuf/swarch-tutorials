"""Checks that the tutorial's arithmetic matches the theory it states."""

from __future__ import annotations

import math

import numpy as np
import pytest
from scipy import stats

from montecarlo.convergence import convergence_grid, interval_coverage
from montecarlo.pi import (
    ERROR_CONSTANT,
    confidence_interval,
    estimate_pi,
    explain_estimate,
    pointwise_band,
    running_estimate,
    samples_needed,
)
from montecarlo.project import (
    DEFAULT_DEADLINE,
    DEFAULT_TASKS,
    Task,
    fastest_total,
    interpret_deadline,
    simulate_project,
    slowest_total,
)


def test_estimate_recovers_pi():
    result = estimate_pi(200_000, seed=1)
    assert abs(result.estimate - math.pi) < 0.015


def test_points_are_classified_by_the_quarter_disk():
    result = estimate_pi(1_000, seed=2)
    assert np.array_equal(result.inside, result.x**2 + result.y**2 <= 1.0)


def test_same_seed_redraws_the_same_darts():
    first = estimate_pi(500, seed=5)
    second = estimate_pi(500, seed=5)
    assert np.array_equal(first.x, second.x)
    assert np.array_equal(first.y, second.y)


def test_running_estimate_ends_at_the_full_estimate():
    result = estimate_pi(300, seed=3)
    running = running_estimate(result.inside)
    assert running[0] in (0.0, 4.0)
    assert running[-1] == pytest.approx(result.estimate)
    assert result.prefix(40).estimate == pytest.approx(running[39])


def test_standard_error_uses_the_bernoulli_formula():
    result = estimate_pi(2_000, seed=4)
    p = result.hit_probability
    expected = 4.0 * math.sqrt(p * (1.0 - p) / result.n)
    assert result.standard_error == pytest.approx(expected)
    assert result.true_standard_error == pytest.approx(ERROR_CONSTANT / math.sqrt(result.n))


def test_sample_standard_error_tracks_the_true_one_at_large_n():
    result = estimate_pi(200_000, seed=1)
    assert result.standard_error == pytest.approx(result.true_standard_error, rel=0.02)


def test_pointwise_band_matches_the_true_standard_error():
    n = 100
    low, high = pointwise_band(n)
    half = confidence_interval(0.0, estimate_pi(n, seed=1).true_standard_error)[1]
    assert high[-1] - math.pi == pytest.approx(half)
    assert math.pi - low[-1] == pytest.approx(half)


def test_tenfold_tighter_band_needs_about_a_hundredfold_more_throws():
    with pytest.raises(ValueError):
        samples_needed(0)
    wide = samples_needed(0.05)
    tight = samples_needed(0.005)
    assert tight / wide == pytest.approx(100, rel=0.01)


def test_interval_string_reports_the_hits():
    result = estimate_pi(100, seed=9)
    text = explain_estimate(result)
    assert f"{result.hits}" in text
    assert f"{result.estimate:.6f}" in text


def test_rmse_times_sqrt_n_stays_near_the_constant():
    grid = convergence_grid([4_000], replications=200, seed=1)
    assert grid.error_times_sqrt_n[0] == pytest.approx(ERROR_CONSTANT, rel=0.15)
    assert grid.estimates.mean() == pytest.approx(math.pi, abs=0.02)


def test_nominal_95_percent_intervals_cover_about_95_percent():
    result = interval_coverage(n=4_000, replications=300, seed=1)
    assert result.degenerate == 0
    assert 0.90 <= result.coverage <= 0.995


def test_task_moments_match_scipy():
    task = Task("Build", 6, 9, 18)
    shape = (9 - 6) / (18 - 6)
    mean, variance = stats.triang.stats(shape, loc=6, scale=12, moments="mv")
    assert task.mean == pytest.approx(float(mean))
    assert task.variance == pytest.approx(float(variance))


def test_default_deadline_sits_between_the_mode_plan_and_the_mean():
    modes = sum(task.mode for task in DEFAULT_TASKS)
    means = sum(task.mean for task in DEFAULT_TASKS)
    assert modes == pytest.approx(16)
    assert means == pytest.approx(20 + 1 / 3)
    assert modes <= DEFAULT_DEADLINE < means


def test_project_totals_stay_inside_the_ranges():
    result = simulate_project(DEFAULT_TASKS, n=5_000, seed=2)
    assert result.totals.min() >= fastest_total(DEFAULT_TASKS) - 1e-9
    assert result.totals.max() <= slowest_total(DEFAULT_TASKS) + 1e-9
    assert result.probability_on_time(fastest_total(DEFAULT_TASKS) - 1) == 0
    assert result.probability_on_time(slowest_total(DEFAULT_TASKS) + 1) == 1


def test_sample_mean_matches_the_formula():
    n = 30_000
    result = simulate_project(DEFAULT_TASKS, n=n, seed=1)
    sigma = math.sqrt(sum(task.variance for task in DEFAULT_TASKS))
    assert result.mean == pytest.approx(result.formula_mean, abs=5 * sigma / math.sqrt(n))


def test_variance_shares_follow_the_triangular_formula():
    result = simulate_project(DEFAULT_TASKS, n=1_000, seed=1)
    total = sum(task.variance for task in DEFAULT_TASKS)
    assert sum(result.variance_share.values()) == pytest.approx(1.0)
    for task in DEFAULT_TASKS:
        assert result.variance_share[task.name] == pytest.approx(task.variance / total)


def test_shared_slip_adds_a_common_delay_to_the_same_tasks():
    base = simulate_project(DEFAULT_TASKS, n=4_000, seed=1, shared_slip=0)
    slipped = simulate_project(DEFAULT_TASKS, n=4_000, seed=1, shared_slip=6)
    difference = slipped.totals - base.totals
    assert np.all(difference >= -1e-8)
    assert np.all(difference <= 6 + 1e-8)
    assert difference.mean() == pytest.approx(3.0, abs=0.08)
    assert "Shared slip" in slipped.variance_share
    assert sum(slipped.variance_share.values()) == pytest.approx(1.0)


def test_percentiles_are_ordered():
    result = simulate_project(DEFAULT_TASKS, n=2_000, seed=3)
    assert result.percentiles[10] <= result.percentiles[50]
    assert result.percentiles[50] <= result.percentiles[80]
    assert result.percentiles[80] <= result.percentiles[90]


def test_default_story_names_the_skew():
    result = simulate_project(DEFAULT_TASKS, n=2_000, seed=1)
    text = interpret_deadline(DEFAULT_TASKS, result, DEFAULT_DEADLINE)
    assert "most-likely" in text
    assert "mean" in text


def test_interpretation_at_the_edges_of_the_ranges():
    result = simulate_project(DEFAULT_TASKS, n=200, seed=1)
    early = interpret_deadline(DEFAULT_TASKS, result, -5)
    late = interpret_deadline(DEFAULT_TASKS, result, 10_000)
    assert "misses" in early
    assert "on time" in late


def test_rejects_a_task_whose_ends_are_inverted():
    with pytest.raises(ValueError):
        Task("Bad", 5, 1, 2)


def test_right_triangle_is_allowed():
    task = Task("Edge", 1, 1, 4)
    result = simulate_project((task,), n=1_000, seed=1)
    assert result.totals.min() >= 1 - 1e-9
    assert result.totals.max() <= 4 + 1e-9
