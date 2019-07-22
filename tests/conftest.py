#!/usr/bin/env python
# -*- coding: utf-8
import os
import shutil
import subprocess

import pytest
import sys


@pytest.fixture(scope="session")
def image_name():
    vi = sys.version_info
    return "mortenlj/dockerma-test", ["{}{}{}".format(version, vi.major, vi.minor) for version in ("v1.0", "latest")]


@pytest.fixture(scope="session")
def images(image_name):
    name, tags = image_name
    def _clean():
        for tag in tags:
            for arch in ("arm", "arm64", "amd64"):
                image = "{}:{}-{}".format(name, tag, arch)
                subprocess.check_output(["docker", "image", "rm", "--force", image],
                                        stderr=subprocess.STDOUT, universal_newlines=True)

    _clean()
    yield
    _clean()


@pytest.fixture
def manifests(image_name):
    name, tags = image_name
    def _clean():
        for tag in tags:
            manifest_name = "docker.io_{}-{}".format(name.replace("/", "_"), tag)
            manifest_path = os.path.join(os.path.expanduser("~/.docker/manifests"), manifest_name)
            shutil.rmtree(manifest_path, ignore_errors=True)
    _clean()
    yield
    _clean()
