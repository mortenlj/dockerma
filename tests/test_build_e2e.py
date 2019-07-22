#!/usr/bin/env python
# -*- coding: utf-8

import subprocess
import tempfile
import textwrap

import pytest


class TestBuildE2E(object):
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
