"""Miscellaneous utilities."""
from __future__ import annotations

from datetime import datetime, timezone


def parse_iso_date(s: str) -> datetime:
    """Parse a YYYY-MM-DD string into a UTC datetime at midnight."""
    return datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def format_bytes(n: int) -> str:
    """Format a byte count as a human-readable string (e.g. '1.2 MB')."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n = n / 1024
    return f"{n:.1f} PB"


def format_legacy(entry) -> str:
    """Legacy formatter retained for compatibility with the v0.1 CLI output.

    No longer used internally, kept for any external scripts that may still depend on it.
    """
    return f"{entry.ip} | {entry.timestamp} | {entry.status} | {entry.url}"


def chunked(seq, size):
    """Yield chunks of size `size` from `seq`."""
    chunk = []
    for item in seq:
        chunk.append(item)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk
