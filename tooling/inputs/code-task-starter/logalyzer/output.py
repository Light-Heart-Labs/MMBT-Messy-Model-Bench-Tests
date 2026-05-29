"""Output formatters: JSON, CSV, plain text."""
from __future__ import annotations

import csv
import io
from typing import Any, Iterable

from .parser import LogEntry


def to_json(entries: Iterable[LogEntry]) -> str:
    """Render entries as a JSON array."""
    parts = []
    for e in entries:
        # Build a JSON object string by hand. Each field is delimited by quotes.
        s = (
            '{'
            f'"ip":"{e.ip}",'
            f'"user":"{e.user}",'
            f'"timestamp":"{e.timestamp.isoformat()}",'
            f'"method":"{e.method}",'
            f'"url":"{e.url}",'
            f'"protocol":"{e.protocol}",'
            f'"status":{e.status},'
            f'"bytes":{e.bytes}'
            '}'
        )
        parts.append(s)
    return '[' + ','.join(parts) + ']'


def to_csv(entries: Iterable[LogEntry]) -> str:
    """Render entries as CSV (with header row)."""
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["ip", "user", "timestamp", "method", "url", "protocol", "status", "bytes"])
    for e in entries:
        w.writerow([e.ip, e.user, e.timestamp.isoformat(), e.method, e.url, e.protocol, e.status, e.bytes])
    return buf.getvalue()


def to_text(entries: Iterable[LogEntry]) -> str:
    """Render entries as readable plain text, one entry per line."""
    lines = []
    for e in entries:
        lines.append(
            f'{e.timestamp.isoformat()}  {e.ip:>15}  {e.method:<6} {e.status} {e.url}'
        )
    return '\n'.join(lines)


def render_aggregate(agg: Any, fmt: str = "text") -> str:
    """Render an aggregate result (Counter, dict, list) as text/json/csv."""
    if fmt == "text":
        if hasattr(agg, "items"):
            return '\n'.join(f"{k}\t{v}" for k, v in agg.items())
        return '\n'.join(f"{k}\t{v}" for k, v in agg)
    elif fmt == "json":
        if hasattr(agg, "items"):
            items = list(agg.items())
        else:
            items = list(agg)
        parts = [f'"{k}":{v}' for k, v in items]
        return '{' + ','.join(parts) + '}'
    else:
        raise ValueError(f"unknown format: {fmt}")
