#!/usr/bin/env python
# -*- coding: utf-8
import argparse

import mock
import pytest

from dockerma.build import _parse_archs, Builder, UnsupportedArchError, UnsupportedBaseError, InvalidConfigurationError
from dockerma.image import Image


class TestBuild(object):
    @pytest.fixture
    def parser(self):
        return argparse.ArgumentParser()

    @pytest.fixture
    def base_image(self):
        mock_image = mock.create_autospec(Image(None, "name", "tag"), spec_set=True, instance=True)
        mock_image.name = "name"
        mock_image.get_supported_archs.return_value = {"amd64"}
        return mock_image

    @pytest.mark.parametrize("line, archs", (
        ("# dockerma archs:x86:", ["x86"]),
        ("# dockerma archs:386,amd64:", ["386", "amd64"]),
        ("# dockerma archs:arm64,amd64:", ["arm64", "amd64"]),
    ))
    def test_arch_pattern(self, line, archs):
        actual_archs = _parse_archs(line)
        assert sorted(actual_archs) == sorted(archs)

    @pytest.mark.parametrize("line,name,tag,alias", (
        ("FROM nginx", "nginx", None, None),
        ("FROM alpine:3.6", "alpine", "3.6", None),
        ("FROM aws-golang:tip", "aws-golang", "tip", None),
        ("FROM common as build", "common", None, "build"),
        ("FROM gcr.io/google-appengine/php:latest", "gcr.io/google-appengine/php", "latest", None),
        ("FROM gcr.io/google-appengine/python", "gcr.io/google-appengine/python", None, None),
        ("FROM python:2-alpine3.8 as common", "python", "2-alpine3.8", "common"),
    ))
    def test_from_dockerfile(self, parser, line, name, tag, alias):
        builder = Builder(parser)
        image = builder._parse_from(line)
        assert image.name == name
        assert image.tag == tag
        assert image.alias == alias

    @pytest.mark.parametrize("archs, exc", (
        (set(), InvalidConfigurationError),
        ({"ppc"}, UnsupportedArchError),
        ({"arm"}, UnsupportedBaseError)
    ))
    def test_check_for_problems(self, parser, archs, base_image, exc):
        builder = Builder(parser)
        builder._archs = archs
        builder._base_images = {base_image}
        with pytest.raises(exc):
            builder._check_for_problems()
