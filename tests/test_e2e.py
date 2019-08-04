#!/usr/bin/env python
# -*- coding: utf-8
import json
import os
import shutil
import subprocess
import tempfile
import textwrap
from datetime import datetime

import pytest
import sys
from six import text_type


class TestE2E(object):
    @pytest.fixture(scope="session")
    def test_run(self):
        n = datetime.now()
        midnight = n.replace(hour=0, minute=0, second=0, microsecond=0)
        return text_type(int((n - midnight).total_seconds()))

    @pytest.fixture(scope="session")
    def image_name(self, test_run):
        vi = sys.version_info
        return "mortenlj/dockerma-test", ["{}{}{}.{}".format(version, vi.major, vi.minor, test_run) for version in
                                          ("v1.0", "latest")]

    @pytest.fixture(scope="session")
    def images(self, image_name):
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
    def manifests(self, image_name):
        name, tags = image_name

        def _clean():
            for tag in tags:
                manifest_name = "docker.io_{}-{}".format(name.replace("/", "_"), tag)
                manifest_path = os.path.join(os.path.expanduser("~/.docker/manifests"), manifest_name)
                shutil.rmtree(manifest_path, ignore_errors=True)

        _clean()
        yield
        _clean()

    @pytest.fixture
    def dockerfile(self):
        with tempfile.NamedTemporaryFile("w", prefix="Dockerfile-build-e2e-", delete=False) as tfile:
            tfile.write(textwrap.dedent("""\
                # dockerma archs:arm,amd64,arm64:
                FROM redis:5.0.4-alpine3.9 as base
                
                COPY ./README.rst /
                
                FROM base as second
                
                FROM traefik:v1.7.11-alpine as final
                
                COPY --from=base /README.rst /
                
                RUN apk update
                """))
            tfile.flush()
            yield tfile.name

    @pytest.mark.usefixtures("images")
    def test_build(self, dockerfile, image_name):
        name, tags = image_name
        args = [
            "dockerma", "--log-level", "debug", "--debug",
            "build",
            "-f", dockerfile,
            ".",
        ]
        for tag in tags:
            args.extend(("-t", "{}:{}".format(name, tag)))
        subprocess.check_call(args)
        output = subprocess.check_output(["docker", "image", "ls", name], universal_newlines=True)
        for tag in tags:
            for arch in ("arm", "arm64", "amd64"):
                arch_tag = "{}-{}".format(tag, arch)
                assert arch_tag in output

    @pytest.mark.usefixtures("manifests")
    def test_push(self, image_name):
        name, tags = image_name
        v1_image_name = "{}:{}".format(name, tags[0])
        subprocess.check_call(["dockerma", "--log-level", "debug", "--debug", "push", v1_image_name])
        output = subprocess.check_output(["docker", "manifest", "inspect", v1_image_name], universal_newlines=True)
        manifests = json.loads(output)
        assert "manifests" in manifests
        for manifest in manifests["manifests"]:
            assert "platform" in manifest
            assert manifest["platform"]["architecture"] in ("arm", "arm64", "amd64")
        assert subprocess.call(["docker", "--log-level", "debug", "image", "pull", v1_image_name]) == 0
