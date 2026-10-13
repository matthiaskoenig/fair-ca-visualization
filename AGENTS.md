# fair-ca-visualization

Interactive visualization of the FAIR COMBINE Archive Indicators (FAIR-CA): a Streamlit app deployed at https://faircombine.streamlit.app and the python package `fair-ca-visualization` (import `fairvis`, console script `fairvis`) on PyPI. Python 3.14, src layout, built with hatchling; the version is in `pyproject.toml` and `src/fairvis/__init__.py`, kept equal by bump-my-version. The documentation at https://matthiaskoenig.github.io/fair-ca-visualization is built with Zensical from `docs/`.

## Commands

```bash
uv sync                                    # environment from uv.lock, incl. the dev group, fairvis editable
uv run streamlit run src/fairvis/app.py    # the app from the checkout (or ./run_app.sh, or uv run fairvis)
uv run pytest -n auto                      # tests, incl. a headless AppTest of the app
uv run ruff check && uv run ruff format    # lint and format
uv run ty check                            # types, zero diagnostics
uv run zensical serve                      # docs preview at http://localhost:8000
uv run zensical build --clean --strict     # docs build into site/
uv build --no-sources && scripts/smoke_test.sh dist/*.whl   # the app from a fresh wheel install
uv lock                                    # after every dependency change in pyproject.toml
uv run pre-commit install                  # once per checkout
```

## Architecture

- `src/fairvis/app.py`: the Streamlit app with the tabs About, Assess Model, Example Assessments, Indicators. Streamlit Community Cloud runs this file from `main`; keep its path.
- `src/fairvis/data_io.py`: loads assessments (xlsx, first sheet, index `ID`), validates required columns and values (NA, 0, 0.5, 1) with `ValueError`, counts the assessments per indicator.
- `src/fairvis/visualization.py`: plotly bar plot per category and polar bar plots per indicator type.
- `src/fairvis/cli.py`: the `fairvis` script, runs `streamlit run` on the packaged `app.py` with the options of `.streamlit/config.toml`.
- `src/fairvis/settings.py`: paths inside the package. `src/fairvis/data/` holds the template `FAIR_assessment_template.xlsx` and the example assessments `assessments/*.xlsx`, bundled in the wheel.
- `tests/`: pytest; `tests/test_app.py` runs the app headless with `streamlit.testing.v1.AppTest`.

## Conventions

- ty and ruff stay at zero diagnostics; suppress only with a rule specific `# ty: ignore[rule]` and a comment why.
- Type hints and Google style docstrings on every public module, class and function; the API reference is generated from them.
- Never hard wrap markdown: one line per paragraph or list item.
- Never use the em dash character, use "-".
- No agent attribution anywhere: no co-author lines, no "generated with" lines in commits, pull requests, code or docs.
- `uv.lock` is committed; Streamlit Community Cloud installs from it, so there is no `requirements.txt`.
- An example assessment is added as `src/fairvis/data/assessments/<Author><Year>_<substance>.xlsx`, see `docs/adding-assessments.md`.
- Changes are described in `release-notes/<version>.md`, one file per release; a pull request that prepares a release adds the note.

## Git

- `develop` is the default branch and protected: no direct push, every change goes through a pull request whose `tests`, `ruff`, `ty` and `docs` checks pass. `main` tracks the latest release and only CI fast-forwards it.
- Work on a branch, open a pull request with `gh-axi pr create --base develop --title <title> --body <text>` and enable auto-merge with `gh-axi pr merge <number> --squash --auto`.
- Commit only when asked.
- Repository policies live in `.github/rulesets/`; change the JSON and run `.github/rulesets/apply.sh`, do not click in the web interface.
- The release process is in `docs/development.md`.
