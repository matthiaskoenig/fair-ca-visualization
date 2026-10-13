"""Tests of the package metadata."""

import tomllib
from pathlib import Path

import fairvis

ROOT = Path(__file__).parents[1]


def test_version() -> None:
    # kept current by bump-my-version, see .bumpversion.toml
    assert fairvis.__version__ == "0.4.0"


def test_version_of_pyproject() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["version"] == fairvis.__version__


def test_uv_lock_records_the_version() -> None:
    # the uv of Streamlit Community Cloud cannot parse a uv.lock whose project
    # has no version, which uv writes for a dynamic version
    lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    (package,) = [p for p in lock["package"] if p["name"] == "fair-ca-visualization"]
    assert package.get("version") == fairvis.__version__
