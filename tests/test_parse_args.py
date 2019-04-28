#!/usr/bin/env python
# -*- coding: utf-8

from dockerma import parse_args


class TestParseArgs(object):
    def test_ignore_unknown_args(self):
        unknown_args = ["--bogus", "action", "--dummy"]
        options, remaining = parse_args(unknown_args)
        assert remaining == unknown_args
