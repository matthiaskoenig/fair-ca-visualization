"""Tests of loading and validating assessments."""

import io
import math
import re
import zipfile
from collections.abc import Callable

import pandas as pd
import pytest

from fairvis.data_io import (
    MAX_ROWS,
    MAX_UNPACKED_BYTES,
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
    # the message names the problem, not internals of the parser
    with pytest.raises(ValueError, match=r"^The file is no readable xlsx file\.$"):
        load_assessment(io.BytesIO(b"this is not an xlsx file"))


def test_load_assessment_missing_indicator(
    template_df: pd.DataFrame, to_xlsx: ToXlsx
) -> None:
    missing_id = template_df.loc[3, "ID"]
    with pytest.raises(ValueError, match=f"misses the indicators {missing_id}"):
        load_assessment(to_xlsx(template_df.drop(index=3)))


def test_load_assessment_unknown_indicator(
    template_df: pd.DataFrame, to_xlsx: ToXlsx
) -> None:
    df = template_df.copy()
    df.loc[3, "ID"] = "CA-RDA-X9-99M"
    with pytest.raises(ValueError, match="unknown indicators CA-RDA-X9-99M"):
        load_assessment(to_xlsx(df))


def test_load_assessment_duplicate_indicator(
    template_df: pd.DataFrame, to_xlsx: ToXlsx
) -> None:
    df = pd.concat([template_df, template_df.iloc[[3]]], ignore_index=True)
    with pytest.raises(ValueError, match=f"more than once: {template_df.loc[3, 'ID']}"):
        load_assessment(to_xlsx(df))


def test_load_assessment_too_many_rows(
    template_df: pd.DataFrame, to_xlsx: ToXlsx
) -> None:
    rows = MAX_ROWS // len(template_df) + 1
    df = pd.concat([template_df] * rows, ignore_index=True)
    with pytest.raises(ValueError, match=f"more than {MAX_ROWS} rows"):
        load_assessment(to_xlsx(df))


def test_load_assessment_zip_bomb() -> None:
    # a small upload which unpacks to more than MAX_UNPACKED_BYTES
    upload = io.BytesIO()
    with zipfile.ZipFile(upload, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("xl/sharedStrings.xml", b"0" * (MAX_UNPACKED_BYTES + 1))
    assert upload.tell() < 1024**2
    with pytest.raises(ValueError, match="too large when unpacked"):
        load_assessment(upload)


def test_load_assessment_reads_an_upload_after_the_size_check(
    template_df: pd.DataFrame, to_xlsx: ToXlsx
) -> None:
    upload = to_xlsx(template_df)
    upload.seek(5)
    assert len(load_assessment(upload)) == len(template_df)


def test_xml_of_uploads_is_parsed_defused() -> None:
    # openpyxl protects against xml bombs only if defusedxml is installed
    import openpyxl.xml

    assert openpyxl.xml.DEFUSEDXML


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


def test_assessment_class_number_stored_as_text() -> None:
    with pytest.raises(ValueError, match="stored as text"):
        assessment_class("1")


def test_load_indicators_counts_by_id_not_position() -> None:
    models = load_model_assessments()
    shuffled = {model_id: df.iloc[::-1] for model_id, df in models.items()}
    pd.testing.assert_frame_equal(load_indicators(shuffled), load_indicators(models))


def test_load_indicators_rejects_other_indicators() -> None:
    models = load_model_assessments()
    model_id, df = next(iter(models.items()))
    with pytest.raises(ValueError, match=model_id):
        load_indicators({model_id: df.iloc[1:]})
