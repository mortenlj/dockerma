#!/usr/bin/env python
# -*- coding: utf-8

import pytest

from dockerma.build import _parse_from, _parse_archs


class TestBuild(object):
    @pytest.mark.parametrize("line, image, tag", (
        ("FROM nginx", "nginx", None),
        ("FROM nginx:v1.0", "nginx", "v1.0"),
        ("FROM nginx:latest", "nginx", "latest"),
        ("FROM nginx AS example", "nginx", None),
        ("FROM nginx:v1.0 AS example", "nginx", "v1.0"),
        ("FROM nginx:latest AS example", "nginx", "latest"),
    ))
    def test_from_pattern(self, line, image, tag):
        actual_image, actual_tag = _parse_from(line)
        assert actual_image == image
        assert actual_tag == tag

    @pytest.mark.parametrize("line, archs", (
        ("# dockerma archs:x86:", ["x86"]),
        ("# dockerma archs:386,amd64:", ["386", "amd64"]),
        ("# dockerma archs:arm64,amd64:", ["arm64", "amd64"]),
    ))
    def test_arch_pattern(self, line, archs):
        actual_archs = _parse_archs(line)
        assert sorted(actual_archs) == sorted(archs)
