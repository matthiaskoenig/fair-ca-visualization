"""Loading and validation of FAIR assessments and the indicators."""

import zipfile
from collections import Counter
from functools import cache
from numbers import Real
from pathlib import Path
from typing import BinaryIO

import numpy as np
import pandas as pd

from fairvis.console import console
from fairvis.settings import ASSESSMENTS_PATH, TEMPLATE_PATH

REQUIRED_COLUMNS: tuple[str, ...] = (
    "ID",
    "Short",
    "Type",
    "Category",
    "Priority",
    "Indicator",
    "Description",
    "Assessment details",
    "Assessment",
)
"""Columns of the template an assessment needs."""

ASSESSMENT_VALUES: tuple[float, ...] = (0.0, 0.5, 1.0)
"""Allowed assessment values besides NA (not applicable, an empty cell)."""

MAX_ROWS = 1000
"""Rows read from an assessment; the template has one row per indicator, far fewer.

Bounds the work of parsing an upload."""

MAX_UNPACKED_BYTES = 20 * 1024**2
"""Size of the unpacked content of an xlsx file, an assessment has less than 1 MB.

An xlsx file is a zip archive; the limit rejects a zip bomb before it is parsed."""


def assessment_class(value: object) -> int:
    """Class of an assessment value.

    Args:
        value: assessment of an indicator, NaN for NA.

    Returns:
        0 for NA, 1 for 0.0, 2 for 0.5 and 3 for 1.0.

    Raises:
        ValueError: if the value is none of NA, 0, 0.5 and 1.
    """
    if isinstance(value, Real) and not isinstance(value, bool):
        number = float(value)
        if np.isnan(number):
            return 0
        for k, reference in enumerate(ASSESSMENT_VALUES, start=1):
            if np.isclose(number, reference):
                return k
    if isinstance(value, str) and _is_number(value):
        raise ValueError(
            f"assessment value {value!r} is stored as text, enter it as a number"
        )
    raise ValueError(f"assessment value {value!r} is none of NA, 0, 0.5, 1")


def _is_number(text: str) -> bool:
    try:
        float(text)
    except ValueError:
        return False
    return True


@cache
def template_indicator_ids() -> tuple[str, ...]:
    """Indicator ids of the template, in the order of the template.

    Returns:
        the `ID` of every indicator of the template.
    """
    return tuple(pd.read_excel(TEMPLATE_PATH, sheet_name=0)["ID"])


def _listing(ids: list[str], limit: int = 5) -> str:
    shown = ", ".join(ids[:limit])
    return shown if len(ids) <= limit else f"{shown} and {len(ids) - limit} more"


def validate_assessment(df: pd.DataFrame) -> None:
    """Validate the structure and the values of a raw assessment.

    Args:
        df: assessment as read from the xlsx file, before the `ID` index is set.

    Raises:
        ValueError: if a column of the template is missing, the indicators differ
            from the ones of the template or an assessment value is none of NA, 0,
            0.5 and 1.
    """
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(
            f"The assessment misses the columns {', '.join(missing)}. "
            "Fill out the FAIR assessment template."
        )
    ids = [str(indicator_id) for indicator_id in df["ID"]]
    duplicates = sorted(i for i, count in Counter(ids).items() if count > 1)
    if duplicates:
        raise ValueError(
            f"The assessment has indicators more than once: {_listing(duplicates)}."
        )
    template_ids = template_indicator_ids()
    id_set, template_id_set = set(ids), set(template_ids)
    missing_ids = [i for i in template_ids if i not in id_set]
    unknown_ids = [i for i in ids if i not in template_id_set]
    if missing_ids or unknown_ids:
        problems = []
        if missing_ids:
            problems.append(f"misses the indicators {_listing(missing_ids)}")
        if unknown_ids:
            problems.append(f"has unknown indicators {_listing(unknown_ids)}")
        raise ValueError(
            f"The assessment {' and '.join(problems)}. "
            "Fill out the FAIR assessment template."
        )
    for indicator_id, value in zip(df["ID"], df["Assessment"], strict=True):
        try:
            assessment_class(value)
        except ValueError as err:
            raise ValueError(f"Indicator '{indicator_id}': {err}.") from err


def _check_unpacked_size(source: Path | BinaryIO) -> None:
    """Reject an xlsx file whose content is larger than `MAX_UNPACKED_BYTES`.

    zipfile never extracts more than the size an archive declares for a member,
    so the declared sizes bound what parsing the file unpacks.
    """
    try:
        with zipfile.ZipFile(source) as archive:
            unpacked = sum(info.file_size for info in archive.infolist())
    except zipfile.BadZipFile as err:
        raise ValueError("The file is no readable xlsx file.") from err
    finally:
        if not isinstance(source, Path):
            source.seek(0)
    if unpacked > MAX_UNPACKED_BYTES:
        raise ValueError(
            "The file is too large when unpacked "
            f"(more than {MAX_UNPACKED_BYTES // 1024**2} MB)."
        )


def load_assessment(source: Path | BinaryIO) -> pd.DataFrame:
    """Load an assessment from an xlsx file.

    Args:
        source: path of the xlsx file or an uploaded file.

    Returns:
        assessment indexed by the indicator `ID`, without the description columns
        and without columns lacking a header (named `Unnamed: <n>` by pandas).

    Raises:
        ValueError: if the file is no readable xlsx file, unpacks to more than
            `MAX_UNPACKED_BYTES`, has more than `MAX_ROWS` rows or is no valid
            assessment.
    """
    _check_unpacked_size(source)
    try:
        df = pd.read_excel(source, sheet_name=0, nrows=MAX_ROWS + 1)
    except Exception as err:
        raise ValueError("The file is no readable xlsx file.") from err
    if len(df) > MAX_ROWS:
        raise ValueError(
            f"The assessment has more than {MAX_ROWS} rows. "
            "Fill out the FAIR assessment template."
        )
    validate_assessment(df)
    unnamed = [column for column in df.columns if str(column).startswith("Unnamed")]
    return df.set_index("ID").drop(
        columns=["Description", "Assessment details", *unnamed]
    )


def load_model_assessments(
    assessment_dir: Path = ASSESSMENTS_PATH,
) -> dict[str, pd.DataFrame]:
    """Load all model assessments of a directory.

    Args:
        assessment_dir: directory with one xlsx file per model.

    Returns:
        assessments by model id (the file name without suffix), sorted by model id.
    """
    return {
        path.stem: load_assessment(path)
        for path in sorted(assessment_dir.glob("*.xlsx"))
    }


def load_indicators(df_models: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Load the indicators and count their assessments over all models.

    Args:
        df_models: assessments by model id, see `load_model_assessments`.

    Returns:
        indicators indexed by `ID`; the column `Assessment` holds the number of
        models with NA, 0, 0.5 and 1 for the indicator.

    Raises:
        ValueError: if an assessment has other indicators than the template.
    """
    df_indicators = (
        pd.read_excel(TEMPLATE_PATH, sheet_name=0)
        .set_index("ID")
        .drop(columns=["Description", "Assessment details", "Assessment", "Comment"])
    )
    assessments = [[0.0, 0.0, 0.0, 0.0] for _ in range(len(df_indicators))]
    for model_id, df_model in df_models.items():
        if not df_model.index.sort_values().equals(df_indicators.index.sort_values()):
            raise ValueError(
                f"The assessment '{model_id}' has other indicators than the template."
            )
        values = df_model["Assessment"].reindex(df_indicators.index).to_numpy()
        for k, value in enumerate(values):
            assessments[k][assessment_class(value)] += 1.0

    df_indicators["Assessment"] = assessments
    return df_indicators


if __name__ == "__main__":
    df_indicators = load_indicators(load_model_assessments())
    console.rule("Indicators", align="left", style="red")
    console.print(df_indicators)
