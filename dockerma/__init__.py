#!/usr/bin/env python
# -*- coding: utf-8

from pkg_resources import get_distribution, DistributionNotFound


def main():
    try:
        dist = get_distribution("dockerma")
        description = "{} {}".format(dist.project_name, dist.version)
    except DistributionNotFound:
        description = "dockerma <unknown>"
    print("Hello, this is {}".format(description))
