#!/usr/bin/env bash
# poetry_export.sh - (executable) generate requirements.txt from pyproject.toml
set -eEuo pipefail
DIR=$(cd "${0%/*}/.." && pwd)
#. "$DIR/scripts/utils.sh"
test -z "${DEBUG:-}" || set -x

# cache_setup

# fix lock if it's not up-to-date (ie. pyproject changed)
poetry lock --check &>/dev/null || poetry lock --no-update

# export prod deps
poetry export --without-hashes --output requirements.txt
if [[ -s requirements.txt ]]; then
    # consistent sort, eg. pytest before pytest-cov
    sort requirements.txt | sponge requirements.txt
else
    # only keep requirements.txt if it's not empty
    rm requirements.txt
fi

# export dev deps
# NOTE extras are included as dev deps IFF there is an extra named 'all'
#grep -q tool.poetry.extras pyproject.toml && EXTRAS=(--extras all) || EXTRAS=()
#poetry export --without-hashes --with dev "${EXTRAS[@]}" --output requirements-dev.txt
poetry export --without-hashes --with dev --output requirements-dev.txt
if [[ -s requirements-dev.txt ]]; then
    # consistent sort, eg. pytest before pytest-cov
    sort requirements-dev.txt | sponge requirements-dev.txt
    # exclude prod deps to leave dev-only deps in requirements-dev.txt
    comm -13 requirements.txt requirements-dev.txt | sponge requirements-dev.txt
fi
if [[ ! -s requirements-dev.txt ]]; then
    # only keep requirements-dev.txt if it's not empty
    rm requirements-dev.txt
fi
