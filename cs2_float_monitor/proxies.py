from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class Proxy:
    id: str
    http: Optional[str]
    https: Optional[str]
    cooldown_seconds: float = 2.0
    last_used_at: float = 0.0

    def to_httpx_proxies(self) -> Dict[str, str]:
        proxies: Dict[str, str] = {}
        if self.http:
            proxies["http://"] = self.http
        if self.https:
            proxies["https://"] = self.https
        return proxies


class ProxyRotator:
    def __init__(self, proxies: List[Proxy]):
        self._proxies = proxies
        self._idx = 0

    @classmethod
    def from_file(cls, path: str) -> "ProxyRotator":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        proxies = [
            Proxy(
                id=p.get("id") or str(i),
                http=p.get("http"),
                https=p.get("https"),
                cooldown_seconds=float(p.get("cooldown_seconds", 2.0)),
            )
            for i, p in enumerate(data.get("proxies", []))
        ]
        return cls(proxies)

    def next_available(self) -> Optional[Proxy]:
        if not self._proxies:
            return None
        now = time.time()
        for _ in range(len(self._proxies)):
            proxy = self._proxies[self._idx]
            self._idx = (self._idx + 1) % len(self._proxies)
            if now - proxy.last_used_at >= proxy.cooldown_seconds:
                proxy.last_used_at = now
                return proxy
        return None

