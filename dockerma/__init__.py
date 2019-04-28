#!/usr/bin/env python
# -*- coding: utf-8
import os
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


def parse_args(args=None):
    parser = ArgumentParser(
        description="DockerMA facilitates building multi-arch containers with minimal fuss",
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    return parser.parse_known_args(args)


def main():
    options, remaining_args = parse_args()
    os.execvp("docker", ["docker"] + remaining_args)
