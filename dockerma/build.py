#!/usr/bin/env python
# -*- coding: utf-8
import re

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
        self._alias_lookup = {}
        self._archs = set()

    def __call__(self, docker, options, remaining_args):
        self._docker = docker
        self._options = options
        self._remaining = remaining_args
        self._parse_dockerfile()
        for image in self._base_images.keys():
            if image.name in self._alias_lookup:
                continue
            if not self._archs.issubset(image.get_supported_archs()):
                missing = self._archs - image.get_supported_archs()
                raise BuildError("{} does not support requested arch: {}".format(image, ", ".join(missing)))

    def _parse_dockerfile(self):
        with open(self._options.file) as fobj:
            for line in fobj:
                try:
                    image = Image.from_dockerfile(self._docker, line)
                    if image:
                        self._base_images[image] = {}
                        if image.alias:
                            self._alias_lookup[image.alias] = image
                except ValueError:
                    pass
                archs = _parse_archs(line)
                self._archs.update(archs)


class BuildError(Exception):
    pass
