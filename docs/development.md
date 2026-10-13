# Contributing

Contributions are welcome, e.g., new example assessments, fixes and features. The repository is [matthiaskoenig/fair-ca-visualization](https://github.com/matthiaskoenig/fair-ca-visualization); development happens against the `develop` branch via pull requests.

## Branch model

Two branches are permanent:

- **`develop`** is the default branch and the branch everything is integrated into. The documentation is published from it.
- **`main`** tracks the latest release. It is fast-forwarded to the released commit by the `sync-main` job of the `CI-CD` workflow after the package went to PyPI. [faircombine.streamlit.app](https://faircombine.streamlit.app) is deployed by Streamlit Community Cloud from `main`, so the app, PyPI and `main` always agree. Nothing is developed on `main` and nothing is merged into it by hand.

Work happens on short lived branches off `develop`, which GitHub deletes after the merge. Releases are tagged on `develop`, see [Release](#release).

## Pull requests

Neither branch accepts a direct push, every change goes through a pull request against `develop`. This includes the maintainer, there is no bypass.

A pull request can only be merged once the four required checks are green:

| check | workflow | content |
|---|---|---|
| `tests` | `ci-cd.yml` | the tests on linux, macos and windows, and the app run from the built wheel |
| `ruff` | `ruff.yml` | `ruff check` and `ruff format --check` |
| `ty` | `ty.yml` | `ty check` |
| `docs` | `docs.yml` | the zensical build including the API reference and the agent files |

Further rules: conversations have to be resolved before the merge, the history stays linear (squash or rebase, no merge commits), and the maintainer is the code owner (`.github/CODEOWNERS`) and is requested for review on every pull request. Auto-merge is enabled, so a pull request can be queued and merges as soon as the checks pass.

### Repository policies { #repository-policies }

The protection is implemented with [repository rulesets](https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets) in `.github/rulesets/`, so a change of a policy is reviewed like any other change:

| ruleset | applies to | rules |
|---|---|---|
| `develop.json` | `develop` | pull request required, the four checks above, resolved conversations, linear history, no force push, no deletion, no bypass |
| `main.json` | `main` | linear history, no force push, no deletion; the fast-forward of the release workflow needs none of them |
| `tags.json` | all tags | a tag cannot be deleted or moved, so a release tag keeps pointing at what was released |
| `tag-creation.json` | all tags | only an admin of the repository can create a tag, i.e., start a release |

Changing a policy means changing the json and applying it:

```bash
.github/rulesets/apply.sh
```

The script is idempotent. It also sets the merge settings and the default branch of the repository and the deployment branches of the `github-pages` and `pypi` environments. It needs the [github cli](https://cli.github.com) authenticated as a user with admin permission on the repository.

## Setup development environment

Development needs [uv](https://docs.astral.sh/uv/) and a checkout of the repository:

```bash
git clone https://github.com/matthiaskoenig/fair-ca-visualization.git
cd fair-ca-visualization
uv sync
```

`uv sync` creates the virtual environment in `.venv` from the committed `uv.lock`, installs `fairvis` into it in editable mode and adds the `dev` dependency group (pytest, ruff, ty, pre-commit, bump-my-version, zensical). Streamlit Community Cloud installs the app from the same `uv.lock`, so local development, continuous integration and production use the same versions. After a change of the dependencies in `pyproject.toml` run `uv lock` and commit `uv.lock`.

Install the git hook, which runs ruff and ty on every commit:

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

Run the app from the checkout:

```bash
uv run streamlit run src/fairvis/app.py   # or ./run_app.sh, or uv run fairvis
```

## Testing

```bash
uv run pytest -n auto                    # the full suite on all cores
uv run pytest tests/test_data_io.py      # a single module
```

The suite loads and validates every bundled assessment, renders the figures, runs the app headless with Streamlit's `AppTest` and checks the `fairvis` command and the citation metadata. Continuous integration also builds the wheel and runs the app from a fresh installation of it:

```bash
uv build --no-sources && scripts/smoke_test.sh dist/*.whl
```

## Linting, formatting and type checking

```bash
uv run ruff check     # lint
uv run ruff format    # format
uv run ty check       # types
```

ruff is configured in `.ruff.toml`, ty in `[tool.ty]` in `pyproject.toml`. Warnings of ty are errors, so the code is kept free of diagnostics; suppress an unavoidable diagnostic with a rule specific `# ty: ignore[rule-name]` rather than a blanket comment.

## Documentation

The documentation is built with [Zensical](https://zensical.org/) from the markdown in `docs/`, configured in `zensical.toml`. The API reference is rendered from the docstrings (Google style) by mkdocstrings.

```bash
uv run zensical serve                    # live preview at http://localhost:8000
uv run zensical build --clean --strict   # build into site/
uv run python scripts/llms_txt.py        # llms.txt, llms-full.txt and the markdown of every page
```

Markdown is not hard wrapped: every paragraph and list item is one line.

## Release

A release publishes the package to PyPI, creates the GitHub release, which [Zenodo](https://doi.org/10.5281/zenodo.13755820) archives, and updates the app on Streamlit Community Cloud. Versions follow [semantic versioning](https://semver.org); tags are the bare version, e.g., `0.4.0`.

1. Create the release branch: `git switch -c release/x.y.z develop`.
2. Write `release-notes/x.y.z.md`, see the earlier notes for the format.
3. Run the checks: `uv run pytest -n auto`, `uv run ruff check`, `uv run ty check`.
4. Bump the version, dry run first:
   ```bash
   uvx bump-my-version bump minor --dry-run -vv   # or major, patch
   uvx bump-my-version bump minor
   ```
   This updates `src/fairvis/__init__.py`, `CITATION.cff` and `tests/test_package.py` and commits, without a tag: the pull request rewrites the commit.
5. Push the branch, open a pull request against `develop` and merge it once green.
6. Tag the merged commit on `develop`:
   ```bash
   git switch develop && git pull
   git tag x.y.z && git push origin x.y.z
   ```
   A tag can neither be moved nor deleted, see [Repository policies](#repository-policies).
7. The `CI-CD` workflow tests, checks that the tag equals the version and that the release notes exist, publishes to PyPI, creates the GitHub release and fast-forwards `main`. Streamlit Community Cloud then redeploys [faircombine.streamlit.app](https://faircombine.streamlit.app).
8. Check the release: `uv tool install --force fair-ca-visualization==x.y.z && fairvis`, and every tab of the production app.
9. Once Zenodo has archived the release, open a pull request which sets `date-released` in `CITATION.cff`.
