#!/usr/bin/env python
# -*- coding: utf-8
import json
import subprocess

import pytest


class TestPushE2E(object):
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
