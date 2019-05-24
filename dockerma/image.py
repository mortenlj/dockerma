#!/usr/bin/env python
# -*- coding: utf-8

import json
import logging
import subprocess

LOG = logging.getLogger(__name__)


class Image(object):
    def __init__(self, docker, name, tag, alias=None, is_alias=False):
        self._docker = docker
        self.name = name
        self.tag = tag
        self.alias = alias
        self.is_alias = is_alias
        self._archs = None

    @property
    def ref(self):
        if self.tag:
            return "{}:{}".format(self.name, self.tag)
        return self.name

    def sha(self, arch):
        if self.is_alias:
            return self.ref
        if self._archs is None:
            self._find_arch_bases()
        return "{}@{}".format(self.name, self._archs[arch])

    def _find_arch_bases(self):
        self._archs = {}
        try:
            output = self._docker.get_output("manifest", "inspect", self.ref)
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
        LOG.debug("{} supports {} archs: {}".format(self, len(self._archs), ", ".join(self._archs.keys())))

    def get_supported_archs(self):
        if self._archs is None:
            self._find_arch_bases()
        return self._archs.keys()

    def __str__(self):
        return self.ref
