"""Experimental features. Not yet wired into the CLI.

Keep this file untouched for now — it's part of an in-progress feature.
"""
from __future__ import annotations

from collections import defaultdict


def detect_anomalies(entries):
    """Naive z-score-based anomaly detection over per-minute request counts.

    Returns minutes whose count is more than 3 standard deviations above the mean.
    """
    counts: dict = defaultdict(int)
    for e in entries:
        bucket = e.timestamp.replace(second=0, microsecond=0)
        counts[bucket] += 1
    if not counts:
        return []
    values = list(counts.values())
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / len(values)
    std = var ** 0.5
    threshold = mean + 3 * std
    return [bucket for bucket, v in counts.items() if v > threshold]


def session_window(entries, window_seconds: int = 1800):
    """Group entries by IP into sessions; a session ends after `window_seconds` of inactivity."""
    by_ip: dict = defaultdict(list)
    for e in entries:
        by_ip[e.ip].append(e)
    sessions = []
    for ip, evs in by_ip.items():
        evs.sort(key=lambda e: e.timestamp)
        cur = [evs[0]]
        for prev, nxt in zip(evs, evs[1:]):
            gap = (nxt.timestamp - prev.timestamp).total_seconds()
            if gap > window_seconds:
                sessions.append((ip, cur))
                cur = []
            cur.append(nxt)
        if cur:
            sessions.append((ip, cur))
    return sessions
