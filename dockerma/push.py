#!/usr/bin/env python
# -*- coding: utf-8

from .build import SUPPORTED_ARCHS


class Pusher(object):
    name = "push"

    def __init__(self, parser):
        parser.add_argument("ref", help="Name and optionally a tag in the 'name:tag' format", metavar="NAME[:TAG]")
        self._docker = None
        self._name = None
        self._tag = None
        self._remaining = []

    def _secondary_init(self, docker, options, remaining_args):
        self._docker = docker
        if ":" in options.ref:
            self._name, self._tag = options.ref.split(":")
        else:
            self._name = options.ref
            self._tag = "latest"
        self._remaining = remaining_args

    def __call__(self, docker, options, remaining_args):
        self._secondary_init(docker, options, remaining_args)
        tags = self._find_valid_tags()
        self._push_tags(tags)
        self._create_manifest(tags)

    def _find_valid_tags(self):
        output = self._docker.get_output("image", "ls", self._name)
        found = []
        for line in output.splitlines():
            name, tag, _ = line.split(None, 2)
            if any(tag == "{}-{}".format(self._tag, arch) for arch in SUPPORTED_ARCHS.keys()):
                found.append("{}:{}".format(name, tag))
        return found

    def _push_tags(self, tags_to_push):
        for tag in tags_to_push:
            self._docker.execute("image", "push", tag, *self._remaining)

    def _create_manifest(self, tags):
        ref = "{}:{}".format(self._name, self._tag)
        self._docker.execute("manifest", "create", ref, *tags)
        self._docker.execute("manifest", "push", ref)
