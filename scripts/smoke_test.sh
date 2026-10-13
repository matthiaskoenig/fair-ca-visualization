#!/usr/bin/env bash
#
# Install a built wheel into a fresh environment and run the app from it, i.e.,
# check the package as a user installs it: the bundled data must be in the wheel
# and the `fairvis` console script must start the server.
#
#   uv build && scripts/smoke_test.sh dist/*.whl
#
set -euo pipefail

WHEEL="$1"
PORT="${PORT:-8599}"
VENV="$(mktemp -d)/venv"
PID=""
# the environment is removed and the server stopped however the script ends
cleanup() {
  if [[ -n "${PID}" ]]; then kill "${PID}" 2>/dev/null || true; fi
  rm -rf "$(dirname "${VENV}")"
}
trap cleanup EXIT

uv venv --quiet --python 3.14 "${VENV}"
uv pip install --quiet --python "${VENV}/bin/python" "${WHEEL}"

# outside the checkout, so nothing is imported from the working tree
cd "$(dirname "${VENV}")"

echo "run the app script of the installed package"
"${VENV}/bin/python" - <<'PY'
from streamlit.testing.v1 import AppTest

from fairvis.data_io import load_model_assessments
from fairvis.settings import APP_PATH

assert "site-packages" in str(APP_PATH), APP_PATH
assert load_model_assessments(), "no bundled assessments"
at = AppTest.from_file(str(APP_PATH), default_timeout=120).run()
assert not at.exception, at.exception
print("app ok:", APP_PATH)
PY

echo "start the server with the console script"
"${VENV}/bin/fairvis" --server.headless=true --server.port="${PORT}" &
PID=$!
curl --silent --fail --retry 30 --retry-delay 2 --retry-all-errors \
  "http://localhost:${PORT}/_stcore/health"
echo
echo "server ok"
