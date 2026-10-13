"""Plotly figures of a FAIR assessment."""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

SUBSET_KEYS: tuple[str, ...] = (
    "Model",
    "Model metadata",
    "Archive",
    "Archive metadata",
)
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


NA_LABEL = "NA (not applicable)"
"""Legend entry of the indicators which do not apply to a model."""

NA_COLOR = "#d9d9d9"
"""Color of the indicators which do not apply to a model, light gray."""


def visualize_barplot(df_data: pd.DataFrame) -> go.Figure:
    """Bar plot of the fraction of the applicable indicators fulfilled per category.

    NA marks an indicator which does not apply to the model; it is not counted. A
    category without applicable indicators has no bar.

    Args:
        df_data: assessment of a model, see `fairvis.data_io.load_assessment`.

    Returns:
        bar plot with the FAIR percentage per category.
    """
    grouped = df_data.groupby("Category", sort=False)["Assessment"]
    df = pd.DataFrame(
        {
            "value": grouped.sum(min_count=0),
            "applicable": grouped.count(),
            "total": grouped.size(),
        }
    )
    df["percentage"] = 100 * df["value"] / df["applicable"].where(df["applicable"] > 0)
    df["label"] = [
        "NA" if np.isnan(p) else f"{p:.0f}%" for p in df["percentage"].to_numpy()
    ]
    df = df.rename_axis("category").reset_index()

    fig = px.bar(
        df,
        x="category",
        y="percentage",
        color="category",
        text="label",
        custom_data=["value", "applicable", "total"],
        color_discrete_sequence=list(COLOR_DISCRETE_SEQUENCE),
        labels={"category": "Category", "percentage": "FAIR [%]"},
    )
    fig.update_traces(
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{x}</b>: %{y:.0f}%<br>"
            "%{customdata[0]:g} of %{customdata[1]} applicable indicators"
            "<br>%{customdata[2]} indicators<extra></extra>"
        ),
    )
    fig.update_layout(
        title="FAIR assessment",
        yaxis_range=[0, 110],
        yaxis_tickvals=[0, 25, 50, 75, 100],
        showlegend=False,
        height=300,
    )

    return fig


def visualize_polar_barplots(df_data: pd.DataFrame) -> list[go.Figure]:
    """Polar bar plots of the indicators of a model, one per type of indicator.

    An indicator which does not apply to the model (NA) is drawn as a full gray
    bar, so it is distinguishable from an indicator assessed with 0.

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
            hover_data=["Category", "Priority"],
            color_discrete_sequence=list(COLOR_DISCRETE_SEQUENCE),
        )
        df_na = df[df["Assessment"].isna()]
        if not df_na.empty:
            fig.add_trace(
                go.Barpolar(
                    r=[1.0] * len(df_na),
                    theta=list(df_na["Short"]),
                    name=NA_LABEL,
                    marker_color=NA_COLOR,
                    customdata=df_na[["Indicator", "Category", "Priority"]].to_numpy(),
                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>Short=%{theta}<br>"
                        "Category=%{customdata[1]}<br>Priority=%{customdata[2]}<br>"
                        "Assessment=NA (not applicable)<extra></extra>"
                    ),
                )
            )
        fig.update_layout(
            title=key,
            showlegend=True,
            height=520,
            legend={"orientation": "h", "yanchor": "top", "y": -0.1, "title": None},
            # room for the labels of the indicators around the circle
            margin={"t": 60, "b": 60, "l": 70, "r": 70},
        )
        fig.update_polars(
            radialaxis_range=[0, 1],
            # the circles at 0.5 and 1 without labels, which would cover the bars
            radialaxis_tickvals=[0, 0.5, 1],
            radialaxis_showticklabels=False,
            angularaxis_showgrid=True,
            # the order of the template, also for the indicators drawn as NA
            angularaxis_categoryorder="array",
            angularaxis_categoryarray=list(df["Short"]),
        )
        figs.append(fig)

    return figs
