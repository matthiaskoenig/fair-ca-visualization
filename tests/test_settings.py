"""Tests of the paths of the bundled data."""

from pathlib import Path

import fairvis
from fairvis import settings


def test_data_is_inside_the_package() -> None:
    package = Path(fairvis.__file__).parent
    assert settings.DATA_PATH.parent == package
    assert settings.APP_PATH == package / "app.py"


def test_bundled_files_exist() -> None:
    assert settings.TEMPLATE_PATH.is_file()
    assert settings.APP_PATH.is_file()
    assert sorted(settings.ASSESSMENTS_PATH.glob("*.xlsx"))
