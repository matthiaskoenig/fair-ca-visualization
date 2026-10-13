"""Tests of the export of an assessment as one figure."""

import pandas as pd
import plotly.graph_objects as go
import pytest

from fairvis import SOFTWARE_DOI, __version__
from fairvis.data_io import load_model_assessments
from fairvis.export import EXPORT_FORMATS, combined_figure, figure_bytes
from fairvis.visualization import NA_LABEL, SUBSET_KEYS

MODELS = load_model_assessments()
MODEL_ID = "BioModels_C19_curated"

# the first bytes of a file of each format
SIGNATURES = {
    "png": b"\x89PNG\r\n\x1a\n",
    "jpeg": b"\xff\xd8\xff",
    "svg": b"<svg",
    "pdf": b"%PDF",
}


@pytest.fixture(scope="module")
def fig() -> go.Figure:
    return combined_figure(MODELS[MODEL_ID], MODEL_ID)


def test_combined_figure_has_all_plots(fig: go.Figure) -> None:
    assert [trace.type for trace in fig.data].count("bar") == 4
    polars = {trace.subplot for trace in fig.data if trace.type == "barpolar"}
    assert polars == {"polar", "polar2", "polar3", "polar4"}
    titles = [annotation.text for annotation in fig.layout.annotations]
    assert all(key in titles for key in SUBSET_KEYS)


def test_combined_figure_keeps_the_polar_axes(fig: go.Figure) -> None:
    # the order of the indicators of each type, not one shared order
    for k, key in enumerate(SUBSET_KEYS):
        polar = fig.layout[f"polar{k + 1 if k else ''}"]
        df = MODELS[MODEL_ID]
        assert list(polar.angularaxis.categoryarray) == list(
            df[df["Type"] == key]["Short"]
        )
        assert tuple(polar.radialaxis.range) == (0, 1)


def test_combined_figure_has_one_legend(fig: go.Figure) -> None:
    names = [trace.name for trace in fig.data if trace.showlegend is not False]
    assert len(names) == len(set(names))
    assert {"Findable", "Accessible", "Interoperable", "Reusable"} <= set(names)


def test_combined_figure_legend_shows_na() -> None:
    df = MODELS[MODEL_ID].copy()
    df.loc[df.index[0], "Assessment"] = float("nan")
    fig = combined_figure(df, MODEL_ID)
    names = [trace.name for trace in fig.data if trace.showlegend is not False]
    assert names.count(NA_LABEL) == 1


def test_combined_figure_is_citable(fig: go.Figure) -> None:
    assert MODEL_ID in fig.layout.title.text
    texts = " ".join(annotation.text for annotation in fig.layout.annotations)
    assert f"fair-ca-visualization {__version__}" in texts
    assert SOFTWARE_DOI in texts


def test_combined_figure_escapes_the_name() -> None:
    # the name of an uploaded file is shown as text, not as plotly markup
    fig = combined_figure(MODELS[MODEL_ID], "<b>model</b>")
    assert "<b>model</b>" not in fig.layout.title.text
    assert "&lt;b&gt;model&lt;/b&gt;" in fig.layout.title.text


def test_combined_figure_does_not_change_the_assessment() -> None:
    df = MODELS[MODEL_ID]
    before = df.copy()
    combined_figure(df, MODEL_ID)
    pd.testing.assert_frame_equal(df, before)


@pytest.mark.parametrize("fmt", list(EXPORT_FORMATS))
def test_figure_bytes(fig: go.Figure, fmt: str) -> None:
    data = figure_bytes(fig, fmt)
    assert data.startswith(SIGNATURES[fmt])


def test_figure_bytes_unknown_format(fig: go.Figure) -> None:
    with pytest.raises(ValueError, match="eps"):
        figure_bytes(fig, "eps")
