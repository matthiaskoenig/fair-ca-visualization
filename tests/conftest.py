"""Shared fixtures of the tests."""

import io
from collections.abc import Callable

import pandas as pd
import pytest

from fairvis.settings import TEMPLATE_PATH


@pytest.fixture
def template_df() -> pd.DataFrame:
    """Raw template as read from the xlsx, one row per indicator."""
    return pd.read_excel(TEMPLATE_PATH, sheet_name=0)


def _to_xlsx(df: pd.DataFrame) -> io.BytesIO:
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer


@pytest.fixture
def to_xlsx() -> Callable[[pd.DataFrame], io.BytesIO]:
    """Write a data frame into an in-memory xlsx file, as an upload provides it."""
    return _to_xlsx
