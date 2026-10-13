"""Headless run of the Streamlit app."""

from streamlit.testing.v1 import AppTest

from fairvis.data_io import load_model_assessments
from fairvis.settings import APP_PATH

TIMEOUT = 120


def test_app_runs() -> None:
    at = AppTest.from_file(str(APP_PATH), default_timeout=TIMEOUT).run()
    assert not at.exception
    assert [tab.label for tab in at.tabs] == [
        "About",
        "Assess Model",
        "Example Assessments",
        "Indicators",
    ]


def test_every_example_model_renders() -> None:
    at = AppTest.from_file(str(APP_PATH), default_timeout=TIMEOUT).run()
    selectbox = at.selectbox[0]
    assert list(selectbox.options) == list(load_model_assessments())
    for model_id in selectbox.options:
        at = selectbox.select(model_id).run()
        assert not at.exception, model_id
        selectbox = at.selectbox[0]
