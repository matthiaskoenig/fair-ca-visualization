"""Plotly figures of a FAIR assessment."""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

SUBSET_KEYS: tuple[str, ...] = ("Model", "Model metadata", "Archive", "Archive metadata")
"""Types of indicators, one polar figure each."""

COLOR_DISCRETE_SEQUENCE: tuple[str, ...] = (
    "#1f77b4",  # muted blue
    "#ff7f0e",  # safety orange
    "#2ca02c",  # cooked asparagus green
    "#d62728",  # brick red
    "#9467bd",  # muted purple
    "#8c564b",  # chestnut brown
    "#e377c2",  # raspberry yogurt pink
    "#7f7f7f",  # middle gray
    "#bcbd22",  # curry yellow-green
    "#17becf",  # blue-teal
)
"""Colors of the categories."""


def visualize_barplot(df_data: pd.DataFrame) -> go.Figure:
    """Bar plot of the fraction of the indicators fulfilled per category.

    Args:
        df_data: assessment of a model, see `fairvis.data_io.load_assessment`.

    Returns:
        bar plot with the FAIR percentage per category.
    """
    # Count the fraction of indicators fullfilled per category
    categories = df_data["Category"].unique()

    values = {k: 0 for k in categories}
    totals = {k: 0 for k in categories}
    for _, row in df_data.iterrows():
        category = row["Category"]
        assessment = row["Assessment"]
        totals[category] += 1.0
        if np.isnan(assessment):
            continue
        else:
            values[category] += assessment

    items = []
    for category in categories:
        items.append(
            {
                "category": category,
                "value": values[category],
                "total": totals[category],
                "percentage": 100 * values[category] / totals[category],
            }
        )

    df = pd.DataFrame(items)

    # barplot
    fig = px.bar(
        df,
        x="category",
        y="percentage",
        color="category",  # title="FAIR assessment",
        color_discrete_sequence=list(COLOR_DISCRETE_SEQUENCE),
        labels=dict(category="Category", percentage="FAIR [%]"),
    )
    fig.update_layout(
        title="FAIR assessment",
        yaxis_range=[0, 100],
        showlegend=False,
        height=250,
    )

    return fig


def visualize_polar_barplots(df_data: pd.DataFrame) -> list[go.Figure]:
    """Polar bar plots of the indicators of a model, one per type of indicator.

    Args:
        df_data: assessment of a model, see `fairvis.data_io.load_assessment`.

    Returns:
        one polar bar plot per entry of `SUBSET_KEYS`, in that order.
    """
    figs = []
    for key in SUBSET_KEYS:
        df = df_data[df_data["Type"] == key]
        fig = px.bar_polar(
            df,
            r="Assessment",
            theta="Short",
            color="Category",
            hover_name="Indicator",
            hover_data=["Indicator", "Category", "Priority"],
            color_discrete_sequence=list(COLOR_DISCRETE_SEQUENCE),
        )
        fig.update_layout(title=key, showlegend=True)
        fig.update_polars(radialaxis_tickvals=[0, 0.5, 1], angularaxis_showgrid=True)
        figs.append(fig)

    return figs
