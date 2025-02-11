"""Scripts for data IO, processing and validation."""

from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
from console import console
from settings import DATA_PATH, TEMPLATE_PATH


def load_model_assessments() -> Dict[str, pd.DataFrame]:
    """Load all model assessment."""
    assessment_dir: Path = DATA_PATH / "assessments"
    df_dict: Dict[str, pd.DataFrame] = {}
    for f_xlsx in assessment_dir.glob("*.xlsx"):
        model_id = f_xlsx.stem
        df = load_assessment(f_xlsx)
        df_dict[model_id] = df

    return df_dict


def load_indicators(df_models: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """"""
    df_indicators = pd.read_excel(TEMPLATE_PATH, sheet_name=0)

    df_indicators.set_index("ID", inplace=True)
    del df_indicators["Description"]
    del df_indicators["Assessment details"]
    del df_indicators["Assessment"]
    del df_indicators["Comment"]

    assessments = [[0.0, 0.0, 0.0, 0.0] for _ in range(len(df_indicators))]
    for model_id, df_model in df_models.items():
        # Count classes
        for k, value in enumerate(df_model["Assessment"].values):
            # console.print(f"{value}, {type(value)}")
            if np.isnan(value):
                k_class = 0
            elif np.isclose(value, 0.0):
                k_class = 1
            elif np.isclose(value, 0.5):
                k_class = 2
            elif np.isclose(value, 1.0):
                k_class = 3

            assessments[k][k_class] = assessments[k][k_class] + 1.0

    # add assessment to indicators
    df_indicators["Assessment"] = assessments
    # console.print(df_indicators)

    return df_indicators


def load_assessment(xlsx_path: Path) -> pd.DataFrame:
    """Load assessment from file."""
    df = pd.read_excel(xlsx_path, sheet_name=0)
    df.set_index("ID", inplace=True)
    del df["Description"]
    del df["Assessment details"]
    # del df["Comment"]
    validate_assessment(df=df)

    return df


def validate_assessment(df: pd.DataFrame) -> None:
    """Validate assessment."""
    pass


if __name__ == "__main__":
    df_models = load_model_assessments()

    df_indicator = load_indicators(df_models)
    console.rule("Indicators", align="left", style="red")
    console.print(df_indicator)
