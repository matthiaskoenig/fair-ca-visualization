"""Console script `fairvis`, starts the app with streamlit.

The options of `.streamlit/config.toml` of the repository are not read when the
app runs from an installed package, so they are passed on the command line.
Further arguments are passed to `streamlit run`, e.g. `fairvis --server.port 8502`.
"""

import sys

from streamlit.web import cli as stcli

from fairvis.settings import APP_PATH

STREAMLIT_OPTIONS: tuple[str, ...] = (
    "--browser.gatherUsageStats=false",
    "--theme.base=light",
)
"""Default options of `streamlit run`, the same as in `.streamlit/config.toml`."""


def streamlit_argv(args: list[str]) -> list[str]:
    """Command line of `streamlit run` for the app.

    Args:
        args: further arguments for `streamlit run`; they follow the defaults,
            so they override them.

    Returns:
        the arguments, starting with the program name `streamlit`.
    """
    return ["streamlit", "run", str(APP_PATH), *STREAMLIT_OPTIONS, *args]


def main() -> None:
    """Start the FAIR-CA visualization app."""
    sys.argv = streamlit_argv(sys.argv[1:])
    sys.exit(stcli.main())
