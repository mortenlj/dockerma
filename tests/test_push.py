#!/usr/bin/env python
# -*- coding: utf-8
import argparse
import textwrap

import mock
import pytest

from dockerma import Pusher

REF = "mortenlj/dockerma-test:v1.0"


class TestPush(object):
    @pytest.fixture
    def parser(self):
        return argparse.ArgumentParser()

    @pytest.fixture
    def docker(self):
        return mock.NonCallableMock()

    @pytest.fixture
    def options(self):
        return mock.NonCallableMock(ref=REF)

    @pytest.fixture
    def pusher(self, parser):
        return Pusher(parser)

    @pytest.mark.parametrize("name,tag,ref", (
            ("name", "tag", "name:tag"),
            ("example", "latest", "example"),
            ("biff", "latest", "biff:latest"),
    ))
    def test_ref_parsing(self, pusher, name, tag, ref):
        options = mock.NonCallableMock(ref=ref)
        pusher._secondary_init(None, options, [])
        assert pusher._name == name
        assert pusher._tag == tag

    def test_find_valid_tags(self, pusher, docker, options):
        docker.get_output.return_value = textwrap.dedent("""\
        REPOSITORY               TAG                 IMAGE ID            CREATED             SIZE
        mortenlj/dockerma-test   latest-arm          c54478b267f4        4 weeks ago         76.9MB
        mortenlj/dockerma-test   v1.0.1-arm          c54478b267f4        4 weeks ago         76.9MB
        mortenlj/dockerma-test   latest-arm64        8f0166413023        4 weeks ago         83.8MB
        mortenlj/dockerma-test   v1.0-arm64          8f0166413023        4 weeks ago         83.8MB
        mortenlj/dockerma-test   latest-amd64        3023c5e47f8c        4 weeks ago         80.1MB
        mortenlj/dockerma-test   v1.0-amd64          3023c5e47f8c        4 weeks ago         80.1MB
        """)
        pusher._secondary_init(docker, options, [])
        actual = pusher._find_valid_tags()
        assert sorted(actual) == [
            "mortenlj/dockerma-test:v1.0-amd64",
            "mortenlj/dockerma-test:v1.0-arm64",
        ]

    def test_push_tags(self, pusher, docker, options):
        tags = ["mortenlj/dockerma-test:latest-arm", "mortenlj/dockerma-test:latest-arm64"]
        pusher._secondary_init(docker, options, [])
        pusher._push_tags(tags)
        assert docker.execute.call_args_list == [
            mock.call("image", "push", "mortenlj/dockerma-test:latest-arm"),
            mock.call("image", "push", "mortenlj/dockerma-test:latest-arm64"),
        ]

    def test_create_manifest(self, pusher, docker, options):
        tags = ["mortenlj/dockerma-test:latest-arm", "mortenlj/dockerma-test:latest-arm64"]
        pusher._secondary_init(docker, options, [])
        pusher._create_manifest(tags)
        assert docker.execute.call_args_list == [
            mock.call("manifest", "create", REF, *tags),
            mock.call("manifest", "push", REF)
        ]
