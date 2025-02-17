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
    # FAIR COMBINE Archive Indicators Visualization
    """
)
tab_about, tab_models, tab_indicators, tab_assessment = st.tabs(
    ["About", "Models", "Indicators", "Assess your Model"]
)

with tab_about:
    st.markdown(
        """
        Computational models are essential tools for studying complex systems which,
        particularly in clinical settings, need to be quality-approved and transparent.
        A community-driven approach to enhance the transparency and communication of
        model features is adherence to the principles of Findability, Accessibility,
        Interoperability and Reusability (FAIR). We propose here an adaptation of the
        FAIR indicators published by the Research Data Alliance to assess the
        FAIRness of models encoded in domain-specific standards, such as those
        established by [COMBINE](https://co.mbine.org).

        The FAIR COMBINE Archive Indicators project is available from [https://github.com/FAIR-CA-indicators/FAIR-CA-indicators.github.io](https://github.com/FAIR-CA-indicators/FAIR-CA-indicators.github.io).

        ## Example visualization
        The following demonstrates the Model and Model metadata indicators for the
        BioModels_C19_curated example. To browse the FAIR indicators for the example
        models select the **Models Tab** above.
        To browse the indicators select the **Indicators Tab** above.
        """
    )
    figs_example = visualize_polar_barplots(df_data=models["BioModels_C19_curated"])
    col1a, col2a = st.columns(2)
    with col1a:
        st.plotly_chart(figs_example[0])
    with col2a:
        st.plotly_chart(figs_example[1])

    st.markdown(
        """
        ## Assess your model

        To assess your model select the **Assess your Model Tab**.
        """
    )
    st.markdown(
        """
        ## Contributors
        **Optimising research through FAIRification of computational models in biology**

        Irina Balaur[1], David Nickerson[2], Danielle Welter[1], Judith A.H. Wodke[3], Francois Ancien[1], Tom Gebhardt[3], Valentin Grouès[1], Henning Hermjakob[4], Matthias König[5], Nicole Radde[6], Adrien Rougny[1], Reinhard Schneider[1], Rahuman Sheriff[4], Kirubel Biruk Shiferaw[3], Melanie Stefan[7], Venkata Satagopam[1], Dagmar Waltemath[3]

        [1] Luxembourg Centre for Systems Biomedicine (LCSB), University of Luxembourg, Luxembourg
        [2] Auckland Bioengineering Institute, University of Auckland, New Zealand
        [3] Medical Informatics Laboratory, University Medicine Greifswald, Germany
        [4] European Molecular Biology Laboratory, European Bioinformatics Institute (EMBL-EBI), UK
        [5] Institute for Biology, Institute for Theoretical Biology, Humboldt University of Berlin, Germany
        [6] Institute for Stochastics and Applications, University Stuttgart, Germany
        [7] Medical School Berlin, Berlin, Germany

        ## How to cite this tool
        [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.13755820.svg)](https://doi.org/10.5281/zenodo.13755820)

        ## Funding
        Matthias König was supported by the BMBF within ATLAS by grant number 031L0304B and by the German Research Foundation (DFG) within the Research Unit Program FOR 5151 QuaLiPerF by grant number 436883643 and by grant number 465194077 (Priority Programme SPP 2311, Subproject SimLivA).
        """
    )

with tab_indicators:
    st.dataframe(
        data=df_indicators,
        use_container_width=True,
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
        st.plotly_chart(fig_bar, use_container_width=False)

    # plotly plot
    figs = visualize_polar_barplots(df_data=df_model)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(figs[0])
    with col2:
        st.plotly_chart(figs[1])
    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(figs[2])
    with col4:
        st.plotly_chart(figs[3])

    # show dataframe
    st.dataframe(df_model, use_container_width=True)

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
            st.plotly_chart(fig_bar, use_container_width=False)

    if uploaded_xlsx is not None:
        # plotly plot
        figs = visualize_polar_barplots(df_data=df_model_upload)
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(figs[0])
        with col2:
            st.plotly_chart(figs[1])
        col3, col4 = st.columns(2)
        with col3:
            st.plotly_chart(figs[2])
        with col4:
            st.plotly_chart(figs[3])

        # show dataframe
        st.dataframe(df_model_upload, use_container_width=True)

st.divider()
st.markdown(
    """
    © 2024-2025 [Matthias König](https://livermetabolism.com), https://github.com/matthiaskoenig/fair-ca-visualization,  [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.13755820.svg)](https://doi.org/10.5281/zenodo.13755820)
    """
)
