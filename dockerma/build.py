#!/usr/bin/env python
# -*- coding: utf-8
import json
import re
import subprocess

from collections import namedtuple
from pprint import pprint

FROM_PATTERN = re.compile(r"FROM\s+(?P<image>[\w./-]+)(:(?P<tag>[\w.-]+))?(\s+AS \w+)?")
ARCH_PATTERN = re.compile(r"# dockerma archs:(?P<archs>.+):")

# Map from docker archs to qemu arch
SUPPORTED_ARCHS = {
    "amd64": None,
    "arm": "arm",
    "arm64": "aarch64",
    "ppc64le": "ppc64le",
    "s390x": "s390x",
}


class Image(namedtuple("Image", ("name", "tag"))):
    @property
    def ref(self):
        if self.tag:
            return "{}:{}".format(self.name, self.tag)
        return self.name

    def __str__(self):
        return self.ref


def _parse_from(line):
    m = FROM_PATTERN.match(line)
    if m:
        return Image(m.group("image"), m.group("tag"))


def _parse_archs(line):
    m = ARCH_PATTERN.match(line)
    if m:
        archs = m.group("archs")
        return re.split(r"\s*,\s*", archs)
    return tuple()


class Builder(object):
    name = "build"

    def __init__(self, parser):
        parser.add_argument("-f", "--file", help="Name of the Dockerfile", default="Dockerfile")
        parser.add_argument("-t", "--tag", action="append", help="Name and optionally a tag in the 'name:tag' format")
        parser.add_argument("--build-arg", help="Set build-time variables")
        parser.add_argument("path", help="Docker context", metavar="PATH|URL")
        self._docker = None
        self._options = None
        self._remaining = []
        self._base_images = {}
        self._archs = []

    def __call__(self, docker, options, remaining_args):
        self._docker = docker
        self._options = options
        self._remaining = remaining_args
        self._parse_dockerfile()
        for image in self._base_images.keys():
            self._find_arch_bases(image)
            print("Arch bases for {}".format(image))
            pprint(self._base_images[image])
            if not all(arch in self._base_images[image].keys() for arch in self._archs):
                print("One or more requested archs are not supported in {}".format(image))

    def _parse_dockerfile(self):
        with open(self._options.file) as fobj:
            for line in fobj:
                image = _parse_from(line)
                if image:
                    self._base_images[image] = {}
                archs = _parse_archs(line)
                self._archs.extend(archs)

    def _find_arch_bases(self, image):
        try:
            output = subprocess.check_output(["docker", "manifest", "inspect", image.ref])
            config = json.loads(output)
            if config["schemaVersion"] != 2 or \
                    config["mediaType"] != "application/vnd.docker.distribution.manifest.list.v2+json":
                print("Base {} has an unsupported manifest".format(image))
                return
            for manifest in config["manifests"]:
                arch = manifest.get("platform", {}).get("architecture")
                digest = manifest.get("digest")
                if arch and digest:
                    self._base_images[image][arch] = digest
        except subprocess.CalledProcessError:
            print("Base {} doesn't support multi-arch".format(image))
