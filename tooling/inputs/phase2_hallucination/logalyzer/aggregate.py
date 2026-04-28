"""Aggregations over log entries."""
from __future__ import annotations

import time
from collections import Counter
from typing import Iterable

from .parser import LogEntry


def by_status(entries: Iterable[LogEntry]) -> Counter:
    """Count entries by HTTP status code."""
    c = Counter()
    for e in entries:
        c[e.status] += 1
    return c


def by_url(entries: Iterable[LogEntry], top: int | None = None) -> list[tuple[str, int]]:
    """Count entries by URL, sorted descending. Optionally truncate to top N."""
    c = Counter(e.url for e in entries)
    items = c.most_common()
    if top is not None:
        items = items[:top]
    return items


def by_hour(entries: Iterable[LogEntry]) -> dict[int, int]:
    """Bucket entries by hour-of-day (0-23) based on their timestamp."""
    buckets: dict[int, int] = {h: 0 for h in range(24)}
    for e in entries:
        # time.localtime takes a unix timestamp; convert from datetime
        ts = e.timestamp.timestamp()
        hour = time.localtime(ts).tm_hour
        buckets[hour] += 1
    return buckets


def total_bytes(entries: Iterable[LogEntry]) -> int:
    """Sum of bytes served across all entries."""
    return sum(e.bytes for e in entries)
