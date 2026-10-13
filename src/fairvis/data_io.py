"""Loading and validation of FAIR assessments and the indicators."""

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
    raise ValueError(f"assessment value {value!r} is none of NA, 0, 0.5, 1")


def validate_assessment(df: pd.DataFrame) -> None:
    """Validate the structure and the values of a raw assessment.

    Args:
        df: assessment as read from the xlsx file, before the `ID` index is set.

    Raises:
        ValueError: if a column of the template is missing or an assessment value
            is none of NA, 0, 0.5 and 1.
    """
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(
            f"The assessment misses the columns {', '.join(missing)}. "
            "Fill out the FAIR assessment template."
        )
    for indicator_id, value in zip(df["ID"], df["Assessment"], strict=True):
        try:
            assessment_class(value)
        except ValueError as err:
            raise ValueError(f"Indicator '{indicator_id}': {err}.") from err


def load_assessment(source: Path | BinaryIO) -> pd.DataFrame:
    """Load an assessment from an xlsx file.

    Args:
        source: path of the xlsx file or an uploaded file.

    Returns:
        assessment indexed by the indicator `ID`, without the description columns
        and without empty unnamed columns.

    Raises:
        ValueError: if the file is no readable xlsx file or no valid assessment.
    """
    try:
        df = pd.read_excel(source, sheet_name=0)
    except Exception as err:
        raise ValueError(f"The file is no readable xlsx file ({err}).") from err
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
    """
    df_indicators = (
        pd.read_excel(TEMPLATE_PATH, sheet_name=0)
        .set_index("ID")
        .drop(columns=["Description", "Assessment details", "Assessment", "Comment"])
    )
    assessments = [[0.0, 0.0, 0.0, 0.0] for _ in range(len(df_indicators))]
    for df_model in df_models.values():
        for k, value in enumerate(df_model["Assessment"].to_numpy()):
            assessments[k][assessment_class(value)] += 1.0

    df_indicators["Assessment"] = assessments
    return df_indicators


if __name__ == "__main__":
    df_indicators = load_indicators(load_model_assessments())
    console.rule("Indicators", align="left", style="red")
    console.print(df_indicators)
