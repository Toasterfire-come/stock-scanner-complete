from __future__ import annotations

import asyncio
import random
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator


async def sleep_with_jitter(base_seconds: float, jitter_fraction: float = 0.2) -> None:
    jitter = base_seconds * jitter_fraction
    delay = base_seconds + random.uniform(-jitter, jitter)
    if delay < 0.0:
        delay = 0.0
    await asyncio.sleep(delay)


class RateLimiter:
    def __init__(self, min_interval_seconds: float) -> None:
        self.min_interval_seconds = min_interval_seconds
        self._last_at = 0.0

    @asynccontextmanager
    async def throttle(self) -> AsyncIterator[None]:
        now = time.time()
        elapsed = now - self._last_at
        if elapsed < self.min_interval_seconds:
            await asyncio.sleep(self.min_interval_seconds - elapsed)
        yield
        self._last_at = time.time()

