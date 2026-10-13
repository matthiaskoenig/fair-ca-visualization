#!/usr/bin/env bash
#
# Apply the repository policies of fair-ca-visualization: the settings of the
# repository, the deployment branches of its environments and the rulesets in
# this directory. The script is idempotent, i.e., a ruleset which already
# exists is updated instead of added a second time, so it can be run again
# after every change of the json files.
#
# The file name of a ruleset has to match the "name" in the json. A ruleset which
# is removed from this directory stays on the repository, delete it with
# `gh api -X DELETE repos/<owner>/<repo>/rulesets/<id>`.
#
# Requires the github cli (https://cli.github.com) authenticated as a user with
# admin permission on the repository:
#
#   gh auth login
#   .github/rulesets/apply.sh [owner/repo]
#
set -euo pipefail

REPO="${1:-matthiaskoenig/fair-ca-visualization}"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "repository settings of ${REPO}"
gh api -X PATCH "repos/${REPO}" \
  -f default_branch=develop \
  -F allow_auto_merge=true \
  -F delete_branch_on_merge=true \
  -F allow_update_branch=true \
  -F allow_squash_merge=true \
  -F allow_rebase_merge=true \
  -F allow_merge_commit=false \
  --silent

# add a deployment branch or tag policy to an environment unless it exists
ensure_policy() {
  local environment="$1" name="$2" type="$3"
  gh api -X PUT "repos/${REPO}/environments/${environment}" --silent --input - <<'JSON'
{"deployment_branch_policy": {"protected_branches": false, "custom_branch_policies": true}}
JSON
  local policies
  policies="$(gh api "repos/${REPO}/environments/${environment}/deployment-branch-policies" \
    --jq ".branch_policies[] | select(.type == \"${type}\") | .name")"
  if grep -qxF "${name}" <<<"${policies}"; then
    echo "environment ${environment}: ${type} ${name} may deploy"
  else
    gh api -X POST "repos/${REPO}/environments/${environment}/deployment-branch-policies" \
      -f name="${name}" -f type="${type}" --silent
    echo "environment ${environment}: ${type} ${name} may deploy (added)"
  fi
}

# GitHub Pages is built by the documentation workflow, not from a branch
if gh api "repos/${REPO}/pages" --silent 2>/dev/null; then
  gh api -X PUT "repos/${REPO}/pages" -f build_type=workflow --silent
else
  gh api -X POST "repos/${REPO}/pages" -f build_type=workflow --silent
fi
echo "GitHub Pages built by GitHub Actions"

# the documentation workflow deploys from develop
ensure_policy github-pages develop branch
# the release workflow publishes to PyPI from a tag
ensure_policy pypi '*' tag

for path in "${DIR}"/*.json; do
  name="$(basename "${path}" .json)"
  id="$(gh api "repos/${REPO}/rulesets" --jq "map(select(.name == \"${name}\")) | .[0].id // empty")"
  if [[ -n "${id}" ]]; then
    gh api -X PUT "repos/${REPO}/rulesets/${id}" --input "${path}" --silent
    echo "ruleset ${name} updated (${id})"
  else
    id="$(gh api -X POST "repos/${REPO}/rulesets" --input "${path}" --jq .id)"
    echo "ruleset ${name} created (${id})"
  fi
done
