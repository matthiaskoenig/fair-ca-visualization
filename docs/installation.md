# Installation

The app runs in the browser at [faircombine.streamlit.app](https://faircombine.streamlit.app) without any installation. To run it on your own computer, e.g., to assess unpublished models without uploading them, install the python package.

## From PyPI

The package needs python 3.14. With [uv](https://docs.astral.sh/uv/) the app is installed as a command line tool in an environment of its own:

```bash
uv tool install fair-ca-visualization
fairvis
```

`fairvis` starts the app and opens it in the browser, by default at http://localhost:8501. Options are passed to [`streamlit run`](https://docs.streamlit.io/develop/api-reference/cli/run), e.g., another port:

```bash
fairvis --server.port 8502
```

The defaults are the ones of the deployed app: no usage statistics, the light theme, uploads of at most 1 MB and errors shown without traceback. An option overrides its default, e.g., `fairvis --client.showErrorDetails=full` for the full traceback.

Without uv, install with pip into a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate        # Linux and macOS
.venv\Scripts\activate           # Windows
pip install fair-ca-visualization
fairvis
```

`python -m fairvis` starts the app as well.

The export of figures needs Chrome or Chromium, see [Exporting a figure](usage.md#exporting-a-figure). Without one, download a Chrome for the export into the data directory of your user, where the app finds it:

```bash
uv tool run --from fair-ca-visualization plotly_get_chrome   # or plotly_get_chrome in the activated virtual environment
```

## From a checkout

To run the latest development version:

```bash
git clone https://github.com/matthiaskoenig/fair-ca-visualization.git
cd fair-ca-visualization
uv sync
uv run streamlit run src/fairvis/app.py
```

`./run_app.sh` is a shortcut for the last command. See [Contributing](development.md) for the development setup.
