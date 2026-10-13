"""Tests of the figures."""

import plotly.graph_objects as go
import pytest

from fairvis.data_io import load_model_assessments
from fairvis.visualization import (
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
    assert all(0 <= y <= 100 for y in percentages)


@pytest.mark.parametrize("model_id", list(MODELS))
def test_polar_barplots(model_id: str) -> None:
    figs = visualize_polar_barplots(MODELS[model_id])
    assert len(figs) == len(SUBSET_KEYS) == 4
    assert [fig.layout.title.text for fig in figs] == list(SUBSET_KEYS)
