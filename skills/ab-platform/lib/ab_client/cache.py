# -*- coding: utf-8 -*-
"""缓存管理（AB 平台 skill 内嵌）

兼容目标：Python 2.7+ / Python 3.x
- 避免 pathlib / typing / encoding= 等 Python3-only 特性
"""

from __future__ import absolute_import, division, print_function

import json
import os
import time


class CacheManager(object):
    def __init__(self, cache_dir=".cache", ttl=300):
        self.cache_dir = cache_dir
        self.ttl = ttl
        if not os.path.exists(self.cache_dir):
            try:
                os.makedirs(self.cache_dir)
            except Exception:
                pass

    def _get_cache_path(self, key):
        import hashlib
        try:
            k = key.encode("utf-8")
        except Exception:
            k = str(key)
        h = hashlib.md5(k).hexdigest()
        return os.path.join(self.cache_dir, "%s.json" % h)

    def get(self, key):
        p = self._get_cache_path(key)
        if not os.path.exists(p):
            return None
        try:
            with open(p, "r") as f:
                data = json.load(f)
            if time.time() - data.get("timestamp", 0) > self.ttl:
                try:
                    os.remove(p)
                except Exception:
                    pass
                return None
            return data.get("data")
        except Exception:
            return None

    def set(self, key, value):
        p = self._get_cache_path(key)
        try:
            with open(p, "w") as f:
                json.dump({"timestamp": time.time(), "data": value}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            try:
                import sys
                sys.stderr.write("警告: 无法写入缓存: %s\n" % e)
            except Exception:
                pass
