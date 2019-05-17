#!/usr/bin/env python
# -*- coding: utf-8
import pytest

from dockerma.image import Image


class TestImage(object):
    @pytest.mark.parametrize("name,tag,expected", (
        ("nginx", "v1", "nginx:v1"),
        ("name", None, "name"),
        ("example", "latest", "example:latest"),
    ))
    def test_ref(self, name, tag, expected):
        assert Image(name, tag).ref == expected

    @pytest.mark.parametrize("line,name,tag,alias", (
        ("FROM nginx", "nginx", None, None),
        ("FROM alpine:3.6", "alpine", "3.6", None),
        ("FROM aws-golang:tip", "aws-golang", "tip", None),
        ("FROM common as build", "common", None, "build"),
        ("FROM gcr.io/google-appengine/php:latest", "gcr.io/google-appengine/php", "latest", None),
        ("FROM gcr.io/google-appengine/python", "gcr.io/google-appengine/python", None, None),
        ("FROM python:2-alpine3.8 as common", "python", "2-alpine3.8", "common"),
    ))
    def test_from_dockerfile(self, line, name, tag, alias):
        image = Image.from_dockerfile(line)
        assert image.name == name
        assert image.tag == tag
        assert image.alias == alias
