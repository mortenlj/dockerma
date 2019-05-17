#!/usr/bin/env python
# -*- coding: utf-8
import re
from pprint import pprint

from .image import Image

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
            print("Arch bases for {}".format(image))
            image.get_supported_archs()
            pprint(image._archs)
            if not all(arch in image.get_supported_archs() for arch in self._archs):
                print("One or more requested archs are not supported in {}".format(image))

    def _parse_dockerfile(self):
        with open(self._options.file) as fobj:
            for line in fobj:
                try:
                    image = Image.from_dockerfile(line)
                    if image:
                        self._base_images[image] = {}
                except ValueError:
                    pass
                archs = _parse_archs(line)
                self._archs.extend(archs)
