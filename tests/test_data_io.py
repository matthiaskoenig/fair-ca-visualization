"""Tests of loading and validating assessments."""

import io
import math
import re
from collections.abc import Callable

import pandas as pd
import pytest

from fairvis.data_io import (
    assessment_class,
    load_assessment,
    load_indicators,
    load_model_assessments,
    validate_assessment,
)
from fairvis.settings import ASSESSMENTS_PATH, TEMPLATE_PATH

ToXlsx = Callable[[pd.DataFrame], io.BytesIO]


@pytest.mark.parametrize(
    ("value", "expected"),
    [(math.nan, 0), (0.0, 1), (0, 1), (0.5, 2), (1.0, 3), (1, 3)],
)
def test_assessment_class(value: object, expected: int) -> None:
    assert assessment_class(value) == expected


@pytest.mark.parametrize("value", [0.75, -1.0, 2.0, "yes", None, True])
def test_assessment_class_invalid(value: object) -> None:
    with pytest.raises(ValueError, match=re.escape("none of NA, 0, 0.5, 1")):
        assessment_class(value)


def test_load_model_assessments_sorted() -> None:
    models = load_model_assessments()
    expected = sorted(path.stem for path in ASSESSMENTS_PATH.glob("*.xlsx"))
    assert list(models) == expected
    assert len(models) >= 1


def test_every_assessment_has_the_indicators_of_the_template(
    template_df: pd.DataFrame,
) -> None:
    for model_id, df in load_model_assessments().items():
        assert list(df.index) == list(template_df["ID"]), model_id
        assert "Description" not in df.columns
        assert "Assessment details" not in df.columns


def test_load_assessment_drops_unnamed_columns() -> None:
    for df in load_model_assessments().values():
        assert not [c for c in df.columns if str(c).startswith("Unnamed")]


def test_load_assessment_from_upload(
    template_df: pd.DataFrame, to_xlsx: ToXlsx
) -> None:
    df = load_assessment(to_xlsx(template_df))
    assert df.index.name == "ID"
    assert len(df) == len(template_df)


def test_load_assessment_missing_columns(
    template_df: pd.DataFrame, to_xlsx: ToXlsx
) -> None:
    upload = to_xlsx(template_df.drop(columns=["Assessment", "Category"]))
    # listed in the order of REQUIRED_COLUMNS
    with pytest.raises(ValueError, match="Category, Assessment"):
        load_assessment(upload)


def test_load_assessment_not_xlsx() -> None:
    with pytest.raises(ValueError, match="no readable xlsx file"):
        load_assessment(io.BytesIO(b"this is not an xlsx file"))


def test_validate_assessment_invalid_value(template_df: pd.DataFrame) -> None:
    df = template_df.copy()
    df["Assessment"] = df["Assessment"].astype(object)
    df.loc[3, "Assessment"] = 0.75
    with pytest.raises(ValueError, match=str(df.loc[3, "ID"])):
        validate_assessment(df)


def test_validate_assessment_template_is_valid(template_df: pd.DataFrame) -> None:
    validate_assessment(template_df)


def test_load_indicators_counts() -> None:
    models = load_model_assessments()
    df_indicators = load_indicators(models)
    template = pd.read_excel(TEMPLATE_PATH, sheet_name=0)
    assert list(df_indicators.index) == list(template["ID"])
    for counts in df_indicators["Assessment"]:
        assert len(counts) == 4
        assert sum(counts) == len(models)

    # the counts of a single indicator, recomputed from the assessments
    first_id = df_indicators.index[0]
    values = [df.loc[first_id, "Assessment"] for df in models.values()]
    expected = [0.0, 0.0, 0.0, 0.0]
    for value in values:
        expected[assessment_class(value)] += 1.0
    assert df_indicators.loc[first_id, "Assessment"] == expected
