#!/usr/bin/env python
# -*- coding: utf-8

import json
import logging
import re
import subprocess


LOG = logging.getLogger(__name__)
FROM_PATTERN = re.compile(r"FROM\s+(?P<name>[\w./-]+)(:(?P<tag>[\w.-]+))?(\s+(?:AS|as) (?P<alias>\w+))?")


class Image(object):
    def __init__(self, docker, name, tag, alias=None):
        self._docker = docker
        self.name = name
        self.tag = tag
        self.alias = alias
        self._archs = None

    @classmethod
    def from_dockerfile(cls, docker, line):
        m = FROM_PATTERN.match(line)
        if m:
            groups = m.groupdict()
            return cls(docker, groups["name"], groups["tag"], groups["alias"])
        raise ValueError("Unable to parse image reference from line %r" % line)

    @property
    def ref(self):
        if self.tag:
            return "{}:{}".format(self.name, self.tag)
        return self.name

    def _find_arch_bases(self):
        self._archs = {}
        try:
            output = self._docker.execute("manifest", "inspect", self.ref)
            config = json.loads(output)
            if config["schemaVersion"] != 2 or \
                    config["mediaType"] != "application/vnd.docker.distribution.manifest.list.v2+json":
                LOG.warning("Unknown manifest type for image %s", self)
                return
            for manifest in config["manifests"]:
                arch = manifest.get("platform", {}).get("architecture")
                digest = manifest.get("digest")
                if arch and digest:
                    self._archs[arch] = digest
        except subprocess.CalledProcessError:
            LOG.error("%s doesn't support multi-arch", self)

    def get_supported_archs(self):
        if self._archs is None:
            self._find_arch_bases()
        return self._archs.keys()

    def __str__(self):
        return self.ref
