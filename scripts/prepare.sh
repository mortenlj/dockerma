#!/usr/bin/env bash

set -euo pipefail

apt-get -y -qq update || true
apt-get -y -qq install mercurial
echo "${DOCKER_HUB_PASSWORD}" | docker login -u "${DOCKER_HUB_USER}" --password-stdin
pip install .[ci]
