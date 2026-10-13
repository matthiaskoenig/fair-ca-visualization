"""Export of an assessment as one figure, e.g. for a manuscript.

The figure is rendered by kaleido in a headless Chrome or Chromium, started for
each rendering. The shared server of kaleido is not used: it mixes up the results
of concurrent calls and blocks if no browser is installed.
"""

import html

import kaleido
import pandas as pd
import plotly.graph_objects as go
from choreographer.browsers.chromium import Chromium
from kaleido.errors import ChromeNotFoundError
from plotly.subplots import make_subplots

from fairvis import SOFTWARE_DOI, __version__
from fairvis.visualization import (
    SUBSET_KEYS,
    visualize_barplot,
    visualize_polar_barplots,
)

EXPORT_FORMATS: dict[str, str] = {
    "png": "image/png",
    "jpeg": "image/jpeg",
    "svg": "image/svg+xml",
    "pdf": "application/pdf",
}
"""Formats of the export with their MIME type."""

WIDTH = 1000
"""Width of the exported figure in px, the unit of the vector formats."""

HEIGHT = 1400
"""Height of the exported figure in px."""

SCALE = 3
"""Scale of the raster formats: 3000 px wide, 300 dpi at a width of 10 inch."""


def combined_figure(df_data: pd.DataFrame, name: str) -> go.Figure:
    """One figure of an assessment: the bar plot above the polar bar plots.

    The figure has one legend of the categories and states the version of
    fair-ca-visualization and its DOI, so it can be cited.

    Args:
        df_data: assessment of a model, see `fairvis.data_io.load_assessment`.
        name: name of the assessed model, shown in the title as text.

    Returns:
        the figure, sized for the export.
    """
    fig_bar = visualize_barplot(df_data)
    figs_polar = visualize_polar_barplots(df_data)

    fig = make_subplots(
        rows=3,
        cols=2,
        specs=[
            [{"type": "xy", "colspan": 2}, None],
            [{"type": "polar"}, {"type": "polar"}],
            [{"type": "polar"}, {"type": "polar"}],
        ],
        row_heights=[0.2, 0.4, 0.4],
        # room for the labels of the indicators around the circles
        vertical_spacing=0.07,
        horizontal_spacing=0.15,
        subplot_titles=("FAIR percentage per category", *SUBSET_KEYS),
    )
    for trace in fig_bar.data:
        # the categories are in the legend of the polar bar plots
        fig.add_trace(trace.update(showlegend=False), row=1, col=1)
    fig.update_xaxes(title=None, row=1, col=1)
    fig.update_yaxes(
        title="FAIR [%]",
        range=fig_bar.layout.yaxis.range,
        tickvals=fig_bar.layout.yaxis.tickvals,
        row=1,
        col=1,
    )

    in_legend: set[str] = set()
    for k, fig_polar in enumerate(figs_polar):
        row, col = divmod(k, 2)
        for trace in fig_polar.data:
            # one legend entry per category and for NA, the colors are shared
            trace.update(legendgroup=trace.name, showlegend=trace.name not in in_legend)
            in_legend.add(trace.name)
            fig.add_trace(trace, row=row + 2, col=col + 1)
        # the axes of the plot, the domain is the one of the subplot
        polar = fig_polar.layout.polar.to_plotly_json()
        polar.pop("domain", None)
        fig.update_polars(polar, row=row + 2, col=col + 1)
    # the labels of up to 26 indicators around a circle, without overlap
    fig.update_polars(angularaxis_tickfont_size=10)

    fig.add_annotation(
        text=(f"fair-ca-visualization {__version__}, https://doi.org/{SOFTWARE_DOI}"),
        xref="paper",
        yref="paper",
        x=1,
        y=-0.06,
        xanchor="right",
        yanchor="top",
        showarrow=False,
        font={"size": 11, "color": "#7f7f7f"},
    )
    fig.update_layout(
        title=f"FAIR assessment of {html.escape(name)}",
        template="plotly_white",
        barmode=figs_polar[0].layout.barmode,
        width=WIDTH,
        height=HEIGHT,
        showlegend=True,
        legend={
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": -0.02,
            "yanchor": "top",
            "title": None,
        },
        margin={"t": 80, "b": 110, "l": 80, "r": 80},
    )
    return fig


def browser_available() -> bool:
    """Whether a Chrome or Chromium for the export is installed.

    Returns:
        True if kaleido finds a browser, also one installed with `plotly_get_chrome`.
    """
    return Chromium.find_browser(skip_local=False) is not None


def figure_bytes(fig: go.Figure, fmt: str) -> bytes:
    """Render a figure as a file.

    Args:
        fig: the figure, e.g. of `combined_figure`.
        fmt: format of the file, a key of `EXPORT_FORMATS`.

    Returns:
        the content of the file.

    Raises:
        ValueError: if the format is not one of `EXPORT_FORMATS`.
        RuntimeError: if no Chrome or Chromium is installed.
    """
    if fmt not in EXPORT_FORMATS:
        raise ValueError(
            f"Format '{fmt}' is not supported, use one of {list(EXPORT_FORMATS)}."
        )
    try:
        return kaleido.calc_fig_sync(
            fig.to_dict(),
            opts={
                "format": fmt,
                "width": WIDTH,
                "height": HEIGHT,
                "scale": SCALE if fmt in ("png", "jpeg") else 1,
            },
            # no MathJax, the figures have no LaTeX: no download from a CDN
            kopts={"mathjax": False},
        )
    except ChromeNotFoundError as err:
        raise RuntimeError(
            "The export needs Chrome or Chromium; install one of them, "
            "e.g. with `plotly_get_chrome`."
        ) from err
