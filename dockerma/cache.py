#!/usr/bin/env python
# -*- coding: utf-8
import hashlib
import logging
import os
import shutil

import appdirs
import time
from six.moves import zip_longest
from ucache import Cache, decode_timestamp

LOG = logging.getLogger(__name__)


class FileCache(Cache):
    manual_expire = True

    def __init__(self, name):
        self._cache_dir = os.path.join(appdirs.user_cache_dir("dockerma"), name)
        super(FileCache, self).__init__()

    def _get(self, key):
        entry_path = self._get_entry_path(key)
        return self._get_entry(entry_path)

    def _get_entry(self, entry_path):
        if not os.path.exists(entry_path):
            return None
        with open(entry_path, "rb") as fobj:
            return fobj.read()

    def _get_many(self, keys):
        result = {}
        for key in keys:
            value = self._get(key)
            if value is not None:
                result[key] = value
        return result

    def _set(self, key, value, timeout):
        entry_path = self._get_entry_path(key)
        dir_path = os.path.dirname(entry_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(entry_path, "wb") as fobj:
            fobj.write(value)

    def _set_many(self, data, timeout):
        for key, value in data.items():
            self._set(key, value, timeout)

    def _delete(self, key):
        entry_path = self._get_entry_path(key)
        self._delete_entry(entry_path)

    def _delete_entry(self, entry_path):
        if os.path.exists(entry_path):
            os.unlink(entry_path)
            directory = os.path.dirname(entry_path)
            while len(directory) > 3 and len(os.listdir(directory)) == 0:
                os.unlink(directory)
                directory = os.path.dirname(directory)

    def _delete_many(self, keys):
        for key in keys:
            self._delete(key)

    def _flush(self):
        shutil.rmtree(self._cache_dir)
        return True

    def clean_expired(self, ndays=0):
        timestamp = time.time() - (ndays * 86400)
        n = 0

        for root, dirs, files in os.walk(self._cache_dir):
            for fname in files:
                entry_path = os.path.join(root, fname)
                value = self._get_entry(entry_path)
                ts, _ = decode_timestamp(value)
                if ts <= timestamp:
                    self._delete_entry(entry_path)
                    n += 1
        return n

    def _get_entry_path(self, key):
        entry_key = hashlib.sha256(key).hexdigest()
        args = [iter(entry_key)] * 3
        names = ("".join(z) for z in zip_longest(*args, fillvalue=""))
        return os.path.join(self._cache_dir, *names)
