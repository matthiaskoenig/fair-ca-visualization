"""FAIR COMBINE indicator app.

Webapp for FAIR indicators.
"""

from typing import Dict, Tuple

import pandas as pd
import streamlit as st
from data_io import load_assessment, load_indicators, load_model_assessments
from settings import TEMPLATE_PATH
from visualization import visualize_barplot, visualize_polar_barplots

st.set_page_config(
    page_title="FAIR-CA-Indicators",
    page_icon="🧊",
    layout="wide",
    menu_items={
        "Get help": "mailto:konigmatt@googlemail.com",
        "Report a bug": "https://github.com/FAIR-CA-indicators/fair-ca-visualization.git/issues/new",
        "About": """
        FAIR-CA-Indicators application.
        """,
    },
)
st.markdown(
    """
        <style>
               .block-container {
                    padding-top: 2rem;
                    padding-bottom: 1rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data() -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """Load data."""
    df_models = load_model_assessments()
    df_indicators = load_indicators(df_models=df_models)

    return df_indicators, df_models


df_indicators, models = load_data()


# --- Main ----------------------------------------------------------------------------
st.markdown(
    """
    # Visualize FAIR COMBINE Archive Indicators
    """
)
tab_about, tab_assessment, tab_models, tab_indicators = st.tabs(
    [
        "About",
        "Assess Model",
        "Example Assessments",
        "Indicators",
    ]
)

with tab_about:
    st.markdown(
        """
        ## Motivation
        Computational models are essential tools for studying complex biological systems. In biomedical and clinical contexts in particular, models must be transparent, well-documented, and reproducible** to ensure reliability and reuse.

        A community-driven approach to improving transparency and communication of model characteristics is the adoption of the **FAIR principles**: *Findability, Accessibility, Interoperability, and Reusability*. Building on the FAIR indicators developed by the **Research Data Alliance (RDA)**, we propose an adaptation specifically designed for computational models encoded in domain standards developed within the **[COMBINE](https://co.mbine.org)** community.

        The **FAIR COMBINE Archive Indicators** enable systematic assessment of the FAIRness of models packaged as COMBINE archives and support improved documentation, sharing, and reuse of computational models in the life sciences. More information is available from:

        >*Balaur I., Nickerson D.P., Welter D., Wodke J.A.H., Ancien F., Gebhardt T., Grouès V., Hermjakob H., König M., Radde N., Rougny A., Schneider R., Malik-Sheriff R.S., Shiferaw K.B., Stefan M., Satagopam V., Waltemath D. (2025).*
        >**FAIRification of computational models in biology.**
        >bioRxiv 2025.03.21.644517 (preprint). doi: [10.1101/2025.03.21.644517](https://doi.org/10.1101/2025.03.21.644517)

        ## Usage
        This webpage provides an interactive visualization of the **FAIR COMBINE Archive Indicators**,

        - Use the **Assess Model** tab to assess your own model (a template for the indicators is provided).
        - Use the **Example Assessments** tab to explore FAIR indicator assessments for example models.
        - Use the **Indicators** tab to browse the individual FAIR indicators.

        ## How to cite the visualization tool
        [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.13755820.svg)](https://doi.org/10.5281/zenodo.13755820)

        ## Example visualization
        The example visualization demonstrates the **Model** and **Model Metadata** FAIR indicators using the *BioModels_C19_curated* example.

        ## Funding
        Matthias König was supported by the **German Federal Ministry of Education and Research (BMBF)** within the ATLAS project (grant number 031L0304B) and by the **German Research Foundation (DFG)** within the Research Unit Program **FOR 5151 QuaLiPerF** (grant number 436883643) and the **Priority Programme SPP 2311 (Subproject SimLivA)** (grant number 465194077).
        """
    )
    figs_example = visualize_polar_barplots(df_data=models["BioModels_C19_curated"])
    col1a, col2a = st.columns(2)
    with col1a:
        st.plotly_chart(figs_example[0], key="pchart_example1")
    with col2a:
        st.plotly_chart(figs_example[1], key="pchart_example2")


with tab_indicators:
    st.dataframe(
        data=df_indicators,
        width="stretch",
        column_config={
            "Assessment": st.column_config.BarChartColumn(
                "FAIR Assessment",
                help="Assessment of all models (NA, 0.0, 0.5, 1.0)",
            ),
        },
    )


with tab_models:
    col_select, col_fair, _ = st.columns(3)
    with col_select:
        model_id = st.selectbox(
            "Select model",
            index=0,
            options=list(models.keys()),
        )
        df_model = models[model_id]

    with col_fair:
        fig_bar = visualize_barplot(df_data=df_model)
        st.plotly_chart(fig_bar, width="content", key="pchart_models_bar1")

    # plotly plot
    figs = visualize_polar_barplots(df_data=df_model)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(figs[0], key="pchart_models_col1")
    with col2:
        st.plotly_chart(figs[1], key="pchart_models_col2")
    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(figs[2], key="pchart_models_col3")
    with col4:
        st.plotly_chart(figs[3], key="pchart_models_col4")

    # show dataframe
    st.dataframe(df_model, width="stretch")

with tab_assessment:
    col_upload, col_template, col_fair_upload = st.columns(3, gap="medium")
    with col_upload:
        uploaded_xlsx = st.file_uploader(
            "Upload FAIR model assessment",
            type="xlsx",
            accept_multiple_files=False,
            key=None,
            help=None,
            on_change=None,
            args=None,
            kwargs=None,
            disabled=False,
            label_visibility="visible",
        )
        if uploaded_xlsx is None:
            df_model_upload = None

        else:
            # Can be used wherever a "file-like" object is accepted:
            df_model_upload = load_assessment(uploaded_xlsx)

    with col_template:
        st.html(
            """
            The template for assessment is available here:
            """
        )
        with open(TEMPLATE_PATH, "rb") as f:
            st.download_button(
                "Download FAIR Template",
                f,
                file_name="FAIR_assessment_template.xlsx",
                help="FAIR assessment template. Fill out and reupload for evaluation.",
            )
    with col_fair_upload:
        if df_model_upload is not None:
            fig_bar = visualize_barplot(df_data=df_model_upload)
            st.plotly_chart(fig_bar, width="content")

    if uploaded_xlsx is not None:
        # plotly plot
        figs = visualize_polar_barplots(df_data=df_model_upload)
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(figs[0], key="pchart_assessment_col1")
        with col2:
            st.plotly_chart(figs[1], key="pchart_assessment_col2")
        col3, col4 = st.columns(2)
        with col3:
            st.plotly_chart(figs[2], key="pchart_assessment_col3")
        with col4:
            st.plotly_chart(figs[3], key="pchart_assessment_col4")

        # show dataframe
        st.dataframe(df_model_upload, width="stretch")

st.divider()
st.markdown(
    """
    © 2024-2026 [Matthias König](https://livermetabolism.com) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.13755820.svg)](https://doi.org/10.5281/zenodo.13755820)
    """
)
