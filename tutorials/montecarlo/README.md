# Monte Carlo, from one picture

A short tutorial you can run. It teaches Monte Carlo with two models, both small enough to check.

1. **Estimate π with darts.** The unit square has area 1. The quarter disk inside it has area π/4. The fraction of uniform darts that land in the disk, times 4, estimates π. Because the answer is known, you can watch the error, test the 1/√n rule, and see what a 95% interval actually claims.
2. **A three-task deadline.** Each task has a lowest, a most likely, and a highest duration. Adding the most-likely column gives 16 days. The means add to about 20.3, because a skewed triangle is pulled toward its long side. The chance of finishing by day 18 has no short formula, so the simulation is the answer. The hit is now "finished on time" instead of "landed in the disk". The arithmetic is the same average.

The library is NumPy, SciPy, and Plotly. The dashboard is Streamlit.

## Run the dashboard

From this folder (after installing deps from the repo root):

```bash
streamlit run app.py
```

The sidebar is the lesson order: the idea, one dartboard experiment, the square-root law, the deadline, then what the numbers do and do not mean.

## See the numbers in a terminal

```bash
python -m montecarlo
```

## Run the tests

From the repo root:

```bash
python -m pytest
```

Or from this folder:

```bash
python -m pytest tests
```

The tests lock the teaching claims: the estimator's standard error, the hundredfold cost of a tenfold tighter band, the default deadline sitting between the most-likely plan and the mean, and a shared delay landing on the same task draws.

## Where to read the code

| File | What it is |
| --- | --- |
| `montecarlo/pi.py` | The dartboard estimator, the standard error, the interval, the sample-size formula |
| `montecarlo/convergence.py` | Repeated experiments, RMSE, and interval coverage |
| `montecarlo/project.py` | Triangular tasks, the deadline probability, the reading of the result |
| `app.py` | Dashboard entry point |
| `dashboard/` | One page per lesson, and the Plotly figures |

NumPy draws the uniform darts and does the reductions. SciPy supplies the normal quantile (`scipy.stats.norm.ppf`) and the triangular draws (`scipy.stats.triang`). The SciPy triangle is parameterized by a shape in [0, 1]; `sample_triangular` translates lowest / most likely / highest into that shape.
