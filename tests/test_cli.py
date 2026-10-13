"""Tests of the `fairvis` console script."""

import os
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

from fairvis import cli
from fairvis.settings import APP_PATH


def test_streamlit_argv_defaults() -> None:
    argv = cli.streamlit_argv([])
    assert argv[:3] == ["streamlit", "run", str(APP_PATH)]
    assert "--browser.gatherUsageStats=false" in argv
    assert "--theme.base=light" in argv


def test_options_of_the_repository_config() -> None:
    # `fairvis` runs the app with the options of .streamlit/config.toml
    path = Path(__file__).parents[1] / ".streamlit" / "config.toml"
    config = tomllib.loads(path.read_text(encoding="utf-8"))
    options = {
        f"--{section}.{name}={str(value).lower()}"
        for section, values in config.items()
        for name, value in values.items()
    }
    assert options == set(cli.STREAMLIT_OPTIONS)


def test_user_options_follow_defaults() -> None:
    # streamlit takes the last value of an option, so user options win
    argv = cli.streamlit_argv(["--theme.base=dark", "--server.port", "8502"])
    assert argv[-3:] == ["--theme.base=dark", "--server.port", "8502"]
    assert argv.index("--theme.base=light") < argv.index("--theme.base=dark")


def test_main_runs_streamlit(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []

    def fake_main() -> int:
        calls.append(list(sys.argv))
        return 0

    monkeypatch.setattr(cli.stcli, "main", fake_main)
    monkeypatch.setattr(sys, "argv", ["fairvis", "--server.port", "8502"])
    with pytest.raises(SystemExit) as exit_info:
        cli.main()
    assert exit_info.value.code == 0
    assert calls == [cli.streamlit_argv(["--server.port", "8502"])]


def test_python_m_fairvis_help() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "fairvis", "--help"],
        capture_output=True,
        encoding="utf-8",
        check=False,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert "Usage" in result.stdout


def test_help_without_utf8_stdout() -> None:
    # the help of `streamlit run` contains non ascii characters; a redirected
    # stdout on windows is encoded with the ansi code page, e.g. cp1252
    result = subprocess.run(
        [sys.executable, "-m", "fairvis", "--help"],
        capture_output=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONIOENCODING": "cp1252"},
        check=False,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert "\u2191" in result.stdout
