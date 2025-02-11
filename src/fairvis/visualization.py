"""Create plots for the indicators."""

from typing import List

import numpy as np
import pandas as pd
import plotly.express as px

subset_keys = ["Model", "Model metadata", "Archive", "Archive metadata"]
color_discrete_sequence = [
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
]


def visualize_barplot(df_data: pd.DataFrame) -> List:
    """Visualize overall fair assessment as bar plot.

    Return figure.
    """
    # Count the fraction of indicators fullfilled per category
    categories = df_data["Category"].unique()

    values = {k: 0 for k in categories}
    totals = {k: 0 for k in categories}
    for key, row in df_data.iterrows():
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
    # console.print(df)

    # barplot
    fig = px.bar(
        df,
        x="category",
        y="percentage",
        color="category",  # title="FAIR assessment",
        color_discrete_sequence=color_discrete_sequence,
        labels=dict(category="Category", percentage="FAIR [%]"),
    )
    fig.update_layout(
        title="FAIR assessment",
        yaxis_range=[0, 100],
        showlegend=False,
        height=250,
    )

    return fig


def visualize_polar_barplots(df_data: pd.DataFrame) -> List:
    """Visualize single model as polar bar plots.

    Indicators are split based on Model/Archive and metadata.

    Return polar figures.
    """

    figs = []
    dfs = [df_data[df_data["Type"] == key] for key in subset_keys]
    # polar barplots
    for k, df in enumerate(dfs):
        key = subset_keys[k]

        fig = px.bar_polar(
            df,
            r="Assessment",
            theta="Short",
            color="Category",
            hover_name="Indicator",
            hover_data=[
                "Indicator",
                "Category",
                "Priority",
            ],  # "Description", "Priority"
            color_discrete_sequence=color_discrete_sequence,
        )
        fig.update_layout(
            title=key,
            showlegend=True,
        )
        fig.update_polars(
            radialaxis_tickvals=[0, 0.5, 1],
            angularaxis_showgrid=True,
        )
        figs.append(fig)

    return figs
