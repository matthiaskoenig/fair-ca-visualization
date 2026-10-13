"""Paths of the app and of the data bundled with the package."""

from pathlib import Path

PACKAGE_PATH: Path = Path(__file__).parent
"""Directory of the installed `fairvis` package."""

APP_PATH: Path = PACKAGE_PATH / "app.py"
"""Streamlit script of the app."""

DATA_PATH: Path = PACKAGE_PATH / "data"
"""Data bundled with the package."""

ASSESSMENTS_PATH: Path = DATA_PATH / "assessments"
"""Example assessments, one xlsx file per model."""

TEMPLATE_PATH: Path = DATA_PATH / "FAIR_assessment_template.xlsx"
"""Template of a FAIR assessment, also the definition of the indicators."""

LOGO_PATH: Path = DATA_PATH / "fair-ca-logo.png"
"""Logo of FAIR-CA, the icon of the app."""
