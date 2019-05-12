#!/usr/bin/env python
# -*- coding: utf-8
import subprocess

if __name__ == "__main__":
    pass


class Docker(object):
    def __init__(self, options, remaining):
        self._options = options
        self._remaining = remaining

    def execute(self, *args):
        cmd = ["docker"]
        o = self._options
        for bool_option in ("debug", "tls", "tlsverify"):
            if getattr(o, bool_option):
                cmd.append("--{}".format(bool_option))
        for value_option in ("config", "log_level", "tlscacert", "tlscert", "tlskey"):
            if getattr(o, value_option):
                cmd.append("--{}".format(value_option.replace("_", "-")))
        if o.host:
            for h in o.host:
                cmd.extend(("--host", h))
        cmd.extend(args)
        subprocess.check_call(cmd)
