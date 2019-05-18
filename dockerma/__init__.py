#!/usr/bin/env python
# -*- coding: utf-8

import logging
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from dockerma.build import Builder
from dockerma.docker import Docker


def parse_args(args=None):
    parser = ArgumentParser(
        description="DockerMA facilitates building multi-arch containers with minimal fuss",
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    # Pass through to docker
    parser.add_argument("--config", help="Location of client config files")
    parser.add_argument("-D", "--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("-H", "--host", action="append", help="Daemon socket(s) to connect to")
    parser.add_argument("-l", "--log-level", choices=("debug", "info", "warn", "error", "fatal"),
                        help="Set the logging level", default="info")
    parser.add_argument("--tls", action="store_true", help="Use TLS; implied by --tlsverify")
    parser.add_argument("--tlscacert", help="Trust certs signed only by this CA")
    parser.add_argument("--tlscert", help="Path to TLS certificate file")
    parser.add_argument("--tlskey", help="Path to TLS key file")
    parser.add_argument("--tlsverify", action="store_true", help="Use TLS and verify the remote")
    parser.add_argument("-v", "--version", action="version", version="TODO", help="Print version information and quit")

    subparsers = parser.add_subparsers(dest="command")
    for ActionClass in (Builder,):
        action_parser = subparsers.add_parser(ActionClass.name)
        action = Builder(action_parser)
        action_parser.set_defaults(action=action)
    options, remaining = parser.parse_known_args(args)
    if options.command is None:
        parser.print_help()
    return options, remaining


def main():
    options, remaining_args = parse_args()
    logging.basicConfig(level=options.log_level.upper())
    docker = Docker(options, remaining_args)
    if options.command == "build":
        options.action(docker, options, remaining_args)
