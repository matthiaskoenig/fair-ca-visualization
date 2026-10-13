"""Shared fixtures of the tests."""

import io
from collections.abc import Callable
from pathlib import Path

import pandas as pd
import pytest

from fairvis.settings import TEMPLATE_PATH


@pytest.fixture
def template_df() -> pd.DataFrame:
    """Raw template as read from the xlsx, one row per indicator."""
    return pd.read_excel(TEMPLATE_PATH, sheet_name=0)


@pytest.fixture
def to_xlsx(tmp_path: Path) -> Callable[[pd.DataFrame], io.BytesIO]:
    """Write a data frame into an in-memory xlsx file, as an upload provides it."""

    def write(df: pd.DataFrame) -> io.BytesIO:
        path = tmp_path / "upload.xlsx"
        df.to_excel(path, index=False)
        return io.BytesIO(path.read_bytes())

    return write
