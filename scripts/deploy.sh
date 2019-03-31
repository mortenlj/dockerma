#!/usr/bin/env bash

set -evuo pipefail

set $(hg parent --template "{latesttag} {latesttagdistance}\n")
export TAG=${1}
export DISTANCE=${2}

if [[ "${DISTANCE}" == 1 ]]; then
    echo "Uploading new version ${TAG} to PyPI"
    twine upload --verbose --repository-url "${PYPI_REPOSITORY}" -u "${PYPI_USERNAME}" -p "${PYPI_PASSWORD}" --disable-progress-bar dist/*
fi
