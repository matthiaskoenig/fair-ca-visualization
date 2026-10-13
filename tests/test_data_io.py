"""Tests of loading and validating assessments."""

import io
import math
import re
import zipfile
from collections.abc import Callable
from pathlib import Path

import openpyxl
import pandas as pd
import pytest

from fairvis.data_io import (
    MAX_COLUMNS,
    MAX_ROWS,
    MAX_UNPACKED_BYTES,
    assessment_class,
    load_assessment,
    load_indicators,
    load_model_assessments,
    read_first_sheet,
    validate_assessment,
)
from fairvis.settings import ASSESSMENTS_PATH, TEMPLATE_PATH
from fairvis.visualization import SUBSET_KEYS

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


def test_load_assessment_unsupported_zip() -> None:
    # zipfile raises NotImplementedError for a zip version it cannot extract
    upload = io.BytesIO()
    with zipfile.ZipFile(upload, "w") as archive:
        archive.writestr("xl/workbook.xml", b"<workbook/>")
    data = bytearray(upload.getvalue())
    central = data.index(b"PK\x01\x02")
    data[central + 6 : central + 8] = (99).to_bytes(2, "little")
    with pytest.raises(ValueError, match=r"^The file is no readable xlsx file\.$"):
        load_assessment(io.BytesIO(bytes(data)))


def test_load_assessment_reads_at_most_max_columns(
    template_df: pd.DataFrame, tmp_path: Path
) -> None:
    # a cell in the last column of a sheet would make every row 16384 cells wide
    path = tmp_path / "wide.xlsx"
    template_df.to_excel(path, index=False)
    workbook = openpyxl.load_workbook(path)
    sheet = workbook.worksheets[0]
    for row in range(1, len(template_df) + 2):
        sheet.cell(row=row, column=16384, value="x")
    workbook.save(path)
    df = load_assessment(path)
    assert len(df.columns) < MAX_COLUMNS
    assert len(df) == len(template_df)


def test_load_assessment_rows_without_id(
    template_df: pd.DataFrame, to_xlsx: ToXlsx
) -> None:
    df = template_df.copy()
    df.loc[3, "ID"] = None
    with pytest.raises(ValueError, match="rows without ID"):
        load_assessment(to_xlsx(df))


def test_load_assessment_skips_empty_rows(
    template_df: pd.DataFrame, to_xlsx: ToXlsx
) -> None:
    empty = pd.DataFrame(
        [[None] * len(template_df.columns)], columns=template_df.columns
    )
    df = pd.concat(
        [template_df.iloc[:3], empty, template_df.iloc[3:]], ignore_index=True
    )
    assert len(load_assessment(to_xlsx(df))) == len(template_df)


def test_load_assessment_takes_the_metadata_of_the_template(
    template_df: pd.DataFrame, to_xlsx: ToXlsx
) -> None:
    # only the assessment comes from the upload, the indicators from the template
    df = template_df.copy()
    df.loc[3, ["Short", "Type", "Category"]] = ["S", "Other", None]
    loaded = load_assessment(to_xlsx(df))
    indicator_id = template_df.loc[3, "ID"]
    for column in ["Short", "Type", "Category"]:
        assert loaded.loc[indicator_id, column] == template_df.loc[3, column]


@pytest.mark.parametrize(
    "path", [TEMPLATE_PATH, *sorted(ASSESSMENTS_PATH.glob("*.xlsx"))], ids=str
)
def test_read_first_sheet_has_the_columns_of_pandas(path: Path) -> None:
    # the rows are read at most `MAX_COLUMNS` wide, but not padded to it (#21)
    expected = pd.read_excel(path, sheet_name=0)
    assert list(read_first_sheet(path).columns) == list(expected.columns)


@pytest.mark.parametrize("path", sorted(ASSESSMENTS_PATH.glob("*.xlsx")), ids=str)
def test_load_assessment_agrees_with_pandas(path: Path) -> None:
    expected = pd.read_excel(path, sheet_name=0).set_index("ID")
    df = load_assessment(path)
    pd.testing.assert_series_equal(
        df["Assessment"], expected["Assessment"].astype(float), check_names=False
    )
    assert list(df.index) == list(expected.index)


def test_template_indicators_have_type_and_category(template_df: pd.DataFrame) -> None:
    # an indicator without type is in no polar bar plot
    assert set(template_df["Type"]) == set(SUBSET_KEYS)
    assert set(template_df["Category"]) == {
        "Findable",
        "Accessible",
        "Interoperable",
        "Reusable",
    }


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


def test_load_indicators_columns() -> None:
    df = load_indicators(load_model_assessments())
    assert list(df.columns) == [
        "Short",
        "Type",
        "Category",
        "Subcategory",
        "Priority",
        "Indicator",
        "Assessment",
    ]


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
