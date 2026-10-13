"""Tests of the figures."""

import math

import pandas as pd
import plotly.graph_objects as go
import pytest

from fairvis.data_io import load_model_assessments
from fairvis.visualization import (
    NA_LABEL,
    SUBSET_KEYS,
    visualize_barplot,
    visualize_polar_barplots,
)

MODELS = load_model_assessments()


@pytest.mark.parametrize("model_id", list(MODELS))
def test_barplot(model_id: str) -> None:
    fig = visualize_barplot(MODELS[model_id])
    assert isinstance(fig, go.Figure)
    percentages = [y for trace in fig.data for y in trace.y]
    assert all(0 <= y <= 100 for y in percentages if not math.isnan(y))


@pytest.mark.parametrize("model_id", list(MODELS))
def test_polar_barplots(model_id: str) -> None:
    figs = visualize_polar_barplots(MODELS[model_id])
    assert len(figs) == len(SUBSET_KEYS) == 4
    assert [fig.layout.title.text for fig in figs] == list(SUBSET_KEYS)


def _assessment(category: str, values: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Short": [f"S{k}" for k in range(len(values))],
            "Type": "Model",
            "Category": category,
            "Priority": "Essential",
            "Indicator": [f"indicator {k}" for k in range(len(values))],
            "Assessment": values,
        }
    )


def test_barplot_excludes_na() -> None:
    # NA does not apply to the model, so it does not lower the percentage
    df = pd.concat(
        [
            _assessment("Findable", [1.0, math.nan, 0.0]),
            _assessment("Accessible", [math.nan, math.nan]),
        ]
    )
    fig = visualize_barplot(df)
    y = {trace.x[0]: trace.y[0] for trace in fig.data}
    assert y["Findable"] == 50.0
    # no applicable indicator, no bar
    assert math.isnan(y["Accessible"])


def test_polar_barplots_show_na() -> None:
    df = _assessment("Findable", [1.0, math.nan, 0.0, math.nan])
    fig = visualize_polar_barplots(df)[0]
    (na_trace,) = [trace for trace in fig.data if trace.name == NA_LABEL]
    assert list(na_trace.theta) == ["S1", "S3"]
    assert list(na_trace.r) == [1.0, 1.0]
    # an indicator assessed with 0 has no bar
    assessed = [t for t in fig.data if t.name != NA_LABEL]
    assert "S2" in [theta for trace in assessed for theta in trace.theta]


def test_polar_barplots_without_na() -> None:
    fig = visualize_polar_barplots(_assessment("Findable", [1.0, 0.5]))[0]
    assert NA_LABEL not in [trace.name for trace in fig.data]
