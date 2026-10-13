"""Tests of the package metadata."""

import fairvis


def test_version() -> None:
    # kept current by bump-my-version, see .bumpversion.toml
    assert fairvis.__version__ == "0.3.0"
