"""Headless run of the Streamlit app."""

import io

import pandas as pd
from streamlit.testing.v1 import AppTest
from streamlit.testing.v1.element_tree import FileUploader

from fairvis.data_io import load_model_assessments
from fairvis.settings import APP_PATH, ASSESSMENTS_PATH

TIMEOUT = 120
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def app(**query_params: str) -> AppTest:
    """App run with the query parameters of a link, e.g. `tab`."""
    at = AppTest.from_file(str(APP_PATH), default_timeout=TIMEOUT)
    at.query_params.update(query_params)
    return at.run()


def file_uploader(at: AppTest) -> FileUploader:
    """The file uploader of the Assess Model tab."""
    (uploader,) = at.get("file_uploader")
    assert isinstance(uploader, FileUploader)
    return uploader


def test_app_runs() -> None:
    at = app()
    assert not at.exception
    assert [tab.label for tab in at.tabs] == [
        "About",
        "Assess Model",
        "Example Assessments",
        "Indicators",
    ]


def test_only_the_selected_tab_runs() -> None:
    # the About tab is the default; the widgets of the other tabs are not created
    at = app()
    assert not at.selectbox
    assert len(at.get("plotly_chart")) == 2


def test_upload_is_kept_on_every_tab() -> None:
    # the uploader exists on every tab, so an upload survives switching tabs
    for tab in ["About", "Example Assessments", "Indicators"]:
        assert file_uploader(app(tab=tab))


def test_no_stray_text() -> None:
    # a bare string literal would be rendered by streamlit's magic
    at = app()
    texts = [element.value for element in at.markdown]
    assert not [text for text in texts if "shown on the About tab" in text]


def test_error_messages_are_escaped() -> None:
    at = app(tab="Assess Model")
    content = (ASSESSMENTS_PATH / "PMR_curated.xlsx").read_bytes()
    df = pd.read_excel(io.BytesIO(content))
    df.loc[0, "ID"] = "![x](https://example.org/x.png)"
    upload = io.BytesIO()
    df.to_excel(upload, index=False)
    file_uploader(at).set_value(("assessment.xlsx", upload.getvalue(), XLSX))
    at.run()
    assert "\\!\\[x\\]" in at.error[0].value


def test_every_example_model_renders() -> None:
    at = app(tab="Example Assessments")
    selectbox = at.selectbox[0]
    assert list(selectbox.options) == list(load_model_assessments())
    for model_id in selectbox.options:
        at = selectbox.select(model_id).run()
        assert not at.exception, model_id
        selectbox = at.selectbox[0]


def test_model_from_query_param() -> None:
    at = app(tab="Example Assessments", model="PMR_curated")
    assert not at.exception
    assert at.selectbox[0].value == "PMR_curated"


def test_upload_of_an_assessment() -> None:
    at = app(tab="Assess Model")
    content = (ASSESSMENTS_PATH / "PMR_curated.xlsx").read_bytes()
    file_uploader(at).set_value(("assessment.xlsx", content, XLSX))
    at.run()
    assert not at.exception
    assert not at.error
    assert len(at.dataframe) == 1


def test_upload_of_an_invalid_file() -> None:
    at = app(tab="Assess Model")
    file_uploader(at).set_value(("assessment.xlsx", b"no xlsx", XLSX))
    at.run()
    assert not at.exception
    assert "no readable xlsx file" in at.error[0].value
    assert not at.dataframe


def test_indicators_tab_counts_the_examples() -> None:
    at = app(tab="Indicators")
    assert not at.exception
    df = at.dataframe[0].value
    assert list(df.columns[-4:]) == ["NA", "0", "0.5", "1"]
    assert (
        df[["NA", "0", "0.5", "1"]].sum(axis=1) == len(load_model_assessments())
    ).all()
