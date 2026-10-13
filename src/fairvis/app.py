"""Streamlit app of the FAIR COMBINE Archive Indicators.

Run with `fairvis`, or from a checkout with `streamlit run src/fairvis/app.py`.

Only the selected tab is computed: the tabs track their state, which is bound to
the query parameter `tab`, so a tab can be linked to directly, e.g.
`?tab=Example+Assessments&model=PMR_curated`.
"""

import io
import re
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from fairvis import SOFTWARE_DOI, __version__
from fairvis.data_io import load_assessment, load_indicators, load_model_assessments
from fairvis.export import (
    EXPORT_FORMATS,
    browser_available,
    combined_figure,
    figure_bytes,
)
from fairvis.settings import LOGO_PATH, TEMPLATE_PATH
from fairvis.visualization import visualize_barplot, visualize_polar_barplots

DOCS_URL = "https://matthiaskoenig.github.io/fair-ca-visualization"
REPOSITORY_URL = "https://github.com/matthiaskoenig/fair-ca-visualization"
PAPER_DOI = "10.1038/s41540-026-00828-7"
PAPER_CITATION = (
    "Balaur I., Nickerson D.P., Welter D., Wodke J.A.H., Ancien F., Gebhardt T., "
    "Grouès V., Hermjakob H., König M., Radde N., Rougny A., Schneider R., "
    "Malik-Sheriff R.S., Shiferaw K.B., Stefan M., Satagopam V., Waltemath D. (2026). "
    "**A system for FAIR assessment of computational biology models and simulations "
    "based on RDA indicators.** *npj Systems Biology and Applications*. "
    f"doi:[{PAPER_DOI}](https://doi.org/{PAPER_DOI})"
)
SOFTWARE_CITATION = (
    "König M. **fair-ca-visualization: interactive visualization of the FAIR COMBINE "
    "Archive Indicators.** Zenodo. "
    f"doi:[{SOFTWARE_DOI}](https://doi.org/{SOFTWARE_DOI})"
)
TABS = ("About", "Assess Model", "Example Assessments", "Indicators")
# example assessment of the About tab; no docstring, streamlit would render it
ABOUT_MODEL = "BioModels_C19_curated"

st.set_page_config(
    page_title="FAIR-CA visualization",
    page_icon=str(LOGO_PATH),
    layout="wide",
    menu_items={
        "Get help": DOCS_URL,
        "Report a bug": f"{REPOSITORY_URL}/issues/new",
        "About": f"fair-ca-visualization {__version__}, see [{DOCS_URL}]({DOCS_URL}).",
    },
)
st.html(
    """
    <style>
    /* wide margins only where the screen is wide */
    @media (min-width: 1024px) {
        .block-container { padding-left: 5rem; padding-right: 5rem; }
    }
    .block-container { padding-top: 2rem; padding-bottom: 1rem; }
    @media (max-width: 640px) {
        .block-container h1 { font-size: 1.75rem; }
    }
    </style>
    """
)


def escape_markdown(text: str) -> str:
    """Escape the markdown of a text, e.g., of an uploaded file.

    Args:
        text: text to show with a markdown element such as `st.error`.

    Returns:
        the text with every markdown character escaped by a backslash.
    """
    return re.sub(r"([\\`*_{}\[\]()<>#+\-.!|~$])", r"\\\1", text)


@st.cache_data
def load_data() -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """Load the indicators and the example assessments.

    Returns:
        indicators with the counts of their assessments, and the assessments by
        model id.
    """
    df_models = load_model_assessments()
    df_indicators = load_indicators(df_models=df_models)

    return df_indicators, df_models


@st.cache_data
def example_figures(model_id: str) -> tuple[go.Figure, list[go.Figure]]:
    """Figures of an example assessment, computed once per model.

    Args:
        model_id: id of a bundled example assessment.

    Returns:
        the bar plot and the polar bar plots of the assessment.
    """
    df_model = load_data()[1][model_id]
    return visualize_barplot(df_model), visualize_polar_barplots(df_model)


@st.cache_data(scope="session", max_entries=4)
def uploaded_assessment(data: bytes) -> pd.DataFrame:
    """Load an uploaded assessment, once per content of the file.

    The cache is the one of the session: an upload is never shared between
    sessions and is removed when the session ends.

    Args:
        data: content of the uploaded xlsx file.

    Returns:
        the assessment, see `fairvis.data_io.load_assessment`.

    Raises:
        ValueError: if the file is no valid FAIR assessment; not cached.
    """
    return load_assessment(io.BytesIO(data))


@st.cache_resource
def template_bytes() -> bytes:
    """Content of the FAIR assessment template.

    Returns:
        the xlsx file as bytes.
    """
    return TEMPLATE_PATH.read_bytes()


def show_assessment(figs_polar: list[go.Figure], df: pd.DataFrame, key: str) -> None:
    """Show the polar bar plots and the table of an assessment.

    Args:
        figs_polar: polar bar plots of the types of indicators.
        df: the assessment.
        key: prefix of the element keys, unique per tab.
    """
    for k in range(0, len(figs_polar), 2):
        for column, fig in zip(st.columns(2), figs_polar[k : k + 2], strict=True):
            with column:
                st.plotly_chart(fig, key=f"{key}_polar{k}_{fig.layout.title.text}")
    st.dataframe(df, width="stretch")


def export_figure(df: pd.DataFrame, name: str, key: str) -> None:
    """Download of the figure of an assessment, rendered on click.

    The figure is rendered in a thread of its own, outside of the script run, so
    no streamlit cache is used: a session-scoped cache cannot be read there.

    Args:
        df: the assessment.
        name: name of the assessed model, in the title and the file name.
        key: prefix of the element keys, unique per tab.
    """
    available = browser_available()
    col_format, col_download = st.columns([1, 1], vertical_alignment="bottom")
    with col_format:
        fmt = st.segmented_control(
            "Export format",
            options=list(EXPORT_FORMATS),
            format_func=str.upper,
            default="png",
            required=True,
            key=f"{key}_format",
        )
    with col_download:
        st.download_button(
            "Export figure",
            lambda: figure_bytes(combined_figure(df, name), fmt),
            file_name=f"{name}_FAIR-CA.{fmt}",
            mime=EXPORT_FORMATS[fmt],
            on_click="ignore",
            icon=":material/image:",
            disabled=not available,
            help=None
            if available
            else "The export needs Chrome or Chromium on the server running the app.",
            key=f"{key}_export",
        )
    st.caption(
        "The bar plot and the polar bar plots as one figure, e.g. for a manuscript. "
        f"It states the version of the app, fair-ca-visualization {__version__}; "
        "please cite it as described on the About tab."
    )


df_indicators, models = load_data()

st.title("Visualize FAIR COMBINE Archive Indicators", anchor=False)
tab_about, tab_assessment, tab_models, tab_indicators = st.tabs(
    TABS, key="tab", bind="query-params"
)

if tab_about.open:
    with tab_about:
        st.markdown(
            f"""
            ## Motivation
            Computational models are essential tools for studying complex biological systems. In biomedical and clinical contexts in particular, models must be transparent, well-documented, and **reproducible** to ensure reliability and reuse.

            A community-driven approach to improving transparency and communication of model characteristics is the adoption of the **FAIR principles**: *Findability, Accessibility, Interoperability, and Reusability*. Building on the FAIR indicators developed by the **Research Data Alliance (RDA)**, we propose an adaptation specifically designed for computational models encoded in domain standards developed within the **[COMBINE](https://co.mbine.org)** community.

            The **FAIR COMBINE Archive Indicators** enable systematic assessment of the FAIRness of models packaged as COMBINE archives and support improved documentation, sharing, and reuse of computational models in the life sciences. They are described in:

            > {PAPER_CITATION}

            ## Usage
            This app visualizes assessments with the **FAIR COMBINE Archive Indicators**:

            - **Assess Model**: download the template, assess your model with it and upload it to see the result.
            - **Example Assessments**: explore the assessments of example models.
            - **Indicators**: browse the indicators and how the example models fulfill them.

            The [documentation]({DOCS_URL}) explains the assessment and the figures. The app also runs locally, see the [installation]({DOCS_URL}/installation/).

            ## How to cite
            If you use the FAIR COMBINE Archive Indicators, please cite the publication above. If you use this app, please also cite

            > {SOFTWARE_CITATION}

            ## Funding
            Matthias König was supported by the **German Federal Ministry of Education and Research (BMBF)** within the ATLAS project (grant number 031L0304B) and by the **German Research Foundation (DFG)** within the Research Unit Program **FOR 5151 QuaLiPerF** (grant number 436883643) and the **Priority Programme SPP 2311 (Subproject SimLivA)** (grant number 465194077).

            ## Example
            The **Model** and **Model metadata** indicators of the example assessment *{ABOUT_MODEL}*:
            """
        )
        figs_example = example_figures(ABOUT_MODEL)[1]
        for column, fig in zip(st.columns(2), figs_example[:2], strict=True):
            with column:
                st.plotly_chart(fig, key=f"about_{fig.layout.title.text}")

# the controls of the upload are created on every run, so that the uploaded file
# is kept when the user switches tabs; only the result is computed lazily
with tab_assessment:
    st.markdown(
        """
        1. Download the FAIR assessment template.
        2. Assess your model: enter for every indicator `1` (fulfilled), `0.5` (partially fulfilled), `0` (not fulfilled) or leave the cell empty if the indicator does not apply to your model (NA).
        3. Upload the filled template.
        """
    )
    col_upload, col_bar = st.columns([1, 2], gap="large")
    with col_upload:
        st.download_button(
            "Download FAIR template",
            template_bytes(),
            file_name="FAIR_assessment_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            icon=":material/download:",
            key="template",
        )
        uploaded_xlsx = st.file_uploader(
            "Upload FAIR model assessment",
            type="xlsx",
            accept_multiple_files=False,
            key="upload",
        )
    if tab_assessment.open and uploaded_xlsx is not None:
        upload_name = Path(uploaded_xlsx.name).stem
        try:
            df_upload = uploaded_assessment(uploaded_xlsx.getvalue())
        except ValueError as err:
            st.error(
                "The uploaded file is no valid FAIR assessment. "
                + escape_markdown(str(err))
            )
        else:
            with col_upload:
                export_figure(df_upload, upload_name, key="upload")
            with col_bar:
                st.plotly_chart(visualize_barplot(df_upload), key="upload_bar")
            show_assessment(
                visualize_polar_barplots(df_upload), df_upload, key="upload"
            )

if tab_models.open:
    with tab_models:
        col_select, col_bar = st.columns([1, 2], gap="large")
        with col_select:
            model_id = st.selectbox(
                "Select model",
                options=list(models),
                key="model",
                bind="query-params",
            )
            export_figure(models[model_id], model_id, key="models")
        fig_bar, figs_polar = example_figures(model_id)
        with col_bar:
            st.plotly_chart(fig_bar, key="models_bar")
        show_assessment(figs_polar, models[model_id], key="models")

if tab_indicators.open:
    with tab_indicators:
        counts = pd.DataFrame(
            df_indicators["Assessment"].tolist(),
            index=df_indicators.index,
            columns=["NA", "0", "0.5", "1"],
        ).astype(int)
        st.markdown(
            f"The indicators of the template and the number of the {len(models)} example assessments with NA, 0, 0.5 and 1 for each."
        )
        st.dataframe(
            df_indicators.drop(columns=["Assessment"]).join(counts),
            width="stretch",
            height="content",
            column_config={
                "Subcategory": None,
                "Indicator": st.column_config.TextColumn("Indicator", width=480),
                **{
                    value: st.column_config.NumberColumn(
                        value, help=f"Example assessments with {value}", width=48
                    )
                    for value in counts.columns
                },
            },
        )

st.divider()
st.markdown(
    f"fair-ca-visualization {__version__} · © 2024-2026 [Matthias König](https://livermetabolism.com) · "
    f"[Documentation]({DOCS_URL}) · [Source code]({REPOSITORY_URL}) · "
    f"[![DOI](https://zenodo.org/badge/DOI/{SOFTWARE_DOI}.svg)](https://doi.org/{SOFTWARE_DOI})"
)
