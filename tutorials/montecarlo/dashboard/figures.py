"""Plotly figures for the tutorial. The arithmetic lives in ``montecarlo``."""

from __future__ import annotations

import math

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dashboard.theme import BAND, GOLD, GRID, INK, INSIDE, MUTED, OUTSIDE, TRUTH
from montecarlo.convergence import ConvergenceResult, CoverageResult
from montecarlo.pi import ERROR_CONSTANT, pointwise_band

_MAX_PATH_POINTS = 1_500


def _style(fig: go.Figure, height: int) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=56, r=20, t=48, b=52),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="sans-serif", color=INK, size=14),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRID, zeroline=False, color=INK, automargin=True)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False, color=INK, automargin=True)
    return fig


def _downsample(k: int, limit: int = _MAX_PATH_POINTS) -> np.ndarray:
    if k <= limit:
        return np.arange(k)
    index = np.linspace(0, k - 1, limit).astype(int)
    return np.unique(index)


def _disk_polygon() -> tuple[np.ndarray, np.ndarray]:
    theta = np.linspace(0, math.pi / 2, 256)
    x = np.concatenate(([0.0], np.cos(theta), [0.0]))
    y = np.concatenate(([0.0], np.sin(theta), [0.0]))
    return x, y


def _add_square_and_disk(fig: go.Figure) -> None:
    disk_x, disk_y = _disk_polygon()
    fig.add_trace(
        go.Scatter(
            x=disk_x,
            y=disk_y,
            fill="toself",
            mode="lines",
            line=dict(color=INSIDE, width=2),
            fillcolor="rgba(15, 118, 110, 0.14)",
            name="quarter disk, area π/4",
            hoverinfo="skip",
        )
    )
    fig.add_shape(
        type="rect",
        x0=0,
        y0=0,
        x1=1,
        y1=1,
        line=dict(color=INK, width=1.5),
        layer="above",
    )


def _square_axes(fig: go.Figure) -> None:
    fig.update_xaxes(range=[-0.04, 1.06], title="x", constrain="domain")
    fig.update_yaxes(
        range=[-0.04, 1.06],
        title="y",
        scaleanchor="x",
        scaleratio=1,
        constrain="domain",
    )


def theory_figure(x: np.ndarray, y: np.ndarray, inside: np.ndarray) -> go.Figure:
    """The unit square and quarter disk, with a handful of darts."""
    fig = go.Figure()
    _add_square_and_disk(fig)
    _add_darts(fig, x, y, inside, size=10)
    _style(fig, height=420)
    _square_axes(fig)
    return fig


def dartboard_figure(x: np.ndarray, y: np.ndarray, inside: np.ndarray) -> go.Figure:
    fig = go.Figure()
    _add_square_and_disk(fig)
    _add_darts(fig, x, y, inside, size=7 if x.size < 800 else 5)
    _style(fig, height=440)
    _square_axes(fig)
    return fig


def _add_darts(fig: go.Figure, x: np.ndarray, y: np.ndarray, inside: np.ndarray, size: int) -> None:
    radius = x * x + y * y
    for mask, name, color in (
        (inside, "inside", INSIDE),
        (~inside, "outside", OUTSIDE),
    ):
        fig.add_trace(
            go.Scatter(
                x=x[mask],
                y=y[mask],
                mode="markers",
                name=name,
                marker=dict(color=color, size=size, opacity=0.85),
                customdata=radius[mask],
                hovertemplate="x=%{x:.3f}<br>y=%{y:.3f}<br>x²+y²=%{customdata:.3f}<extra>" + name + "</extra>",
            )
        )


def running_figure(estimate_path: np.ndarray) -> go.Figure:
    """Running π̂ with the pointwise 95% band around the true value."""
    k = int(estimate_path.size)
    low, high = pointwise_band(k)
    half = float(high[-1] - math.pi)
    pad = max(0.35 * half, 0.002)
    y0 = min(float(low[-1]), float(estimate_path[-1])) - pad
    y1 = max(float(high[-1]), float(estimate_path[-1])) + pad
    # Shade the band only once it fits in this window. Earlier, it is several
    # units wide and would paint the whole panel.
    fits = np.flatnonzero((high <= y1) & (low >= y0))
    band_start = int(fits[0]) if fits.size else 0
    band_index = _downsample(k - band_start)
    band_index = band_index + band_start
    path_index = _downsample(k)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=band_index + 1,
            y=low[band_index],
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=band_index + 1,
            y=high[band_index],
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor=BAND,
            name="95% band",
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=path_index + 1,
            y=estimate_path[path_index],
            mode="lines",
            name="running estimate",
            line=dict(color=INSIDE, width=2.4),
            hovertemplate="after %{x:,} darts<br>π̂ = %{y:.4f}<extra></extra>",
        )
    )
    fig.add_hline(y=math.pi, line_color=TRUTH, line_width=1.5, annotation_text="π", annotation_position="right")
    fig.add_trace(
        go.Scatter(
            x=[k],
            y=[estimate_path[-1]],
            mode="markers",
            name="estimate now",
            marker=dict(color=INK, size=9),
            hovertemplate="π̂ = %{y:.4f}<extra></extra>",
        )
    )
    _style(fig, height=440)
    fig.update_xaxes(title="darts counted")
    fig.update_yaxes(title="estimate of π", range=[y0, y1])
    fig.update_layout(hovermode="x unified")
    return fig


def spread_figure(result: ConvergenceResult) -> go.Figure:
    """Box plots of π̂. Each box is a sampling distribution at one n."""
    fig = go.Figure()
    for n, column in zip(result.sample_sizes, result.estimates):
        fig.add_trace(
            go.Box(
                y=column,
                name=f"{int(n):,}",
                marker_color=INSIDE,
                line_color=INSIDE,
                boxpoints="outliers",
            )
        )
    fig.add_hline(
        y=math.pi,
        line_color=TRUTH,
        line_width=1.5,
        annotation_text="π",
        annotation_position="right",
    )
    _style(fig, height=440)
    fig.update_xaxes(title="throws in one experiment")
    fig.update_yaxes(title="estimate of π")
    return fig


def error_figure(result: ConvergenceResult) -> go.Figure:
    """Log-log error, with the 1/√n law and a 1/n line drawn from the same start."""
    sizes = result.sample_sizes.astype(np.float64)
    theory = result.theoretical_se
    # A 1/n curve anchored on the theoretical error at the smallest n,
    # so the two reference lines start together and then diverge.
    linear = theory[0] * (sizes[0] / sizes)
    product = result.error_times_sqrt_n

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.12,
        row_heights=[0.62, 0.38],
    )
    fig.add_trace(
        go.Scatter(
            x=sizes,
            y=result.rmse,
            mode="markers+lines",
            name="empirical RMSE",
            marker=dict(color=INSIDE, size=9),
            line=dict(color=INSIDE, width=2),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=sizes,
            y=theory,
            mode="lines",
            name="theory, C / √n",
            line=dict(color=TRUTH, width=2, dash="dash"),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=sizes,
            y=linear,
            mode="lines",
            name="a 1/n curve, for comparison",
            line=dict(color=MUTED, width=1.5, dash="dot"),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=sizes,
            y=product,
            mode="markers+lines",
            name="RMSE × √n",
            marker=dict(color=INSIDE, size=9),
            line=dict(color=INSIDE, width=2),
            showlegend=False,
        ),
        row=2,
        col=1,
    )
    fig.add_hline(
        y=ERROR_CONSTANT,
        line_color=TRUTH,
        line_dash="dash",
        row=2,
        col=1,
        annotation_text=f"C = {ERROR_CONSTANT:.3f}",
        annotation_position="top left",
    )
    _style(fig, height=640)
    # dtick=1 on a log axis labels powers of ten, which stay readable.
    fig.update_xaxes(type="log", dtick=1, row=1, col=1)
    fig.update_xaxes(type="log", dtick=1, title_text="throws n", row=2, col=1)
    fig.update_yaxes(type="log", dtick=1, title_text="error", row=1, col=1)
    fig.update_yaxes(title_text="error × √n", row=2, col=1)
    fig.update_layout(margin=dict(l=72, t=56, b=48))
    return fig


def coverage_figure(result: CoverageResult, show: int = 36) -> go.Figure:
    """A sample of intervals. Teal segments contain π; orange segments miss it."""
    count = min(show, result.replications)
    low = result.low[:count]
    high = result.high[:count]
    covered = result.covered[:count]
    estimates = result.estimates[:count]
    fig = go.Figure()
    for want, name, color in (
        (True, "covers π", INSIDE),
        (False, "misses π", OUTSIDE),
    ):
        xs: list[float | None] = []
        ys: list[float | None] = []
        for i in np.flatnonzero(covered if want else ~covered):
            xs.extend((float(low[i]), float(high[i]), None))
            ys.extend((float(i + 1), float(i + 1), None))
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=color, width=3), name=name))
    colors = [INSIDE if flag else OUTSIDE for flag in covered]
    fig.add_trace(
        go.Scatter(
            x=estimates,
            y=np.arange(1, count + 1),
            mode="markers",
            marker=dict(color=colors, size=7),
            name="estimate",
            showlegend=False,
            hovertemplate="experiment %{y:.0f}<br>π̂ = %{x:.4f}<extra></extra>",
        )
    )
    fig.add_vline(x=math.pi, line_color=TRUTH, line_width=1.5)
    _style(fig, height=560)
    fig.update_xaxes(title="interval for π")
    fig.update_yaxes(title="experiment", dtick=5)
    return fig


def duration_figure(
    totals: np.ndarray,
    deadline: float,
    sum_of_modes: float,
    percentile_80: float,
) -> go.Figure:
    on_time = totals[totals <= deadline]
    late = totals[totals > deadline]
    start = float(totals.min())
    end = float(totals.max())
    width = max((end - start) / 40.0, 1e-6)
    bins = dict(start=start, end=end + width, size=width)
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(x=on_time, name="on time", marker_color=INSIDE, xbins=bins, hovertemplate="%{x:.1f} days<br>%{y} projects<extra></extra>")
    )
    fig.add_trace(
        go.Histogram(x=late, name="late", marker_color=OUTSIDE, xbins=bins, hovertemplate="%{x:.1f} days<br>%{y} projects<extra></extra>")
    )
    _mark(fig, sum_of_modes, "most-likely plan", MUTED, "dash", 0.98)
    _mark(fig, percentile_80, "80th percentile", INSIDE, "dot", 0.84)
    _mark(fig, deadline, "deadline", GOLD, "solid", 0.70)
    _style(fig, height=460)
    fig.update_layout(barmode="stack")
    fig.update_xaxes(title="total duration (working days)")
    fig.update_yaxes(title="simulated projects")
    return fig


def _mark(fig: go.Figure, x: float, label: str, color: str, dash: str, height: float) -> None:
    fig.add_vline(x=x, line_color=color, line_width=2, line_dash=dash)
    fig.add_annotation(
        x=x,
        y=height,
        yref="paper",
        text=label,
        showarrow=False,
        font=dict(color=color, size=12),
        bgcolor="rgba(247, 246, 243, 0.9)",
    )


def variance_figure(shares: dict[str, float]) -> go.Figure:
    names = list(shares)
    values = np.array([shares[name] for name in names])
    order = np.argsort(values)
    ordered_names = [names[i] for i in order]
    ordered_values = values[order]
    fig = go.Figure(
        go.Bar(
            y=ordered_names,
            x=ordered_values,
            orientation="h",
            marker_color=INSIDE,
            text=[f"{value:.0%}" for value in ordered_values],
            textposition="auto",
            hovertemplate="%{y}<br>%{x:.1%} of the variance<extra></extra>",
        )
    )
    _style(fig, height=320)
    fig.update_xaxes(title="share of variance of the total", tickformat=".0%", range=[0, 1])
    fig.update_yaxes(title="")
    return fig
