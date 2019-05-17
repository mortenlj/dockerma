#!/usr/bin/env python
# -*- coding: utf-8

import pytest

from dockerma.build import _parse_archs


class TestBuild(object):
    @pytest.mark.parametrize("line, archs", (
        ("# dockerma archs:x86:", ["x86"]),
        ("# dockerma archs:386,amd64:", ["386", "amd64"]),
        ("# dockerma archs:arm64,amd64:", ["arm64", "amd64"]),
    ))
    def test_arch_pattern(self, line, archs):
        actual_archs = _parse_archs(line)
        assert sorted(actual_archs) == sorted(archs)
