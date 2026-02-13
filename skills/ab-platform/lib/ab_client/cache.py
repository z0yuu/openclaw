"""
缓存管理（AB 平台 skill 内嵌）
"""

import json
import time
from pathlib import Path
from typing import Any, Optional


class CacheManager:
    def __init__(self, cache_dir: str = ".cache", ttl: int = 300):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl

    def _get_cache_path(self, key: str) -> Path:
        import hashlib
        h = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{h}.json"

    def get(self, key: str) -> Optional[Any]:
        p = self._get_cache_path(key)
        if not p.exists():
            return None
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            if time.time() - data["timestamp"] > self.ttl:
                p.unlink(missing_ok=True)
                return None
            return data["data"]
        except Exception:
            return None

    def set(self, key: str, value: Any) -> None:
        p = self._get_cache_path(key)
        try:
            with open(p, "w", encoding="utf-8") as f:
                json.dump({"timestamp": time.time(), "data": value}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"警告: 无法写入缓存: {e}", file=__import__("sys").stderr)
