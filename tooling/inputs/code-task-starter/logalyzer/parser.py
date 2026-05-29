"""Log line parsing.

Supports Apache Combined Log Format and the Common Log Format.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

# Apache CLF: 127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326
LOG_LINE_RE = re.compile(
    r'^(?P<ip>\S+) \S+ (?P<user>\S+) '
    r'\[(?P<timestamp>[^\]]+)\] '
    r'"(?P<method>[A-Z]+) (?P<url>\S+) (?P<protocol>[^"]+)" '
    r'(?P<status>\d+) (?P<bytes>\S+)'
)

# Apache uses 3-letter abbreviated month names in its timestamps.
MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Aug", "Sep", "Oct", "Nov", "Dec",
]


@dataclass(frozen=True)
class LogEntry:
    ip: str
    user: str
    timestamp: datetime
    method: str
    url: str
    protocol: str
    status: int
    bytes: int


def parse_timestamp(s: str) -> datetime:
    """Parse an Apache-style timestamp like '10/Oct/2000:13:55:36 -0700' to a UTC datetime."""
    # Format: DD/MMM/YYYY:HH:MM:SS [+-]HHMM
    m = re.match(
        r'(\d{2})/(\w{3})/(\d{4}):(\d{2}):(\d{2}):(\d{2}) ([+-]\d{4})',
        s,
    )
    if not m:
        raise ValueError(f"unrecognized timestamp format: {s!r}")
    day, month_str, year, hour, minute, second, tz = m.groups()
    month = MONTH_NAMES.index(month_str) + 1
    # tz like "-0700" → seconds offset
    tz_sign = 1 if tz[0] == "+" else -1
    tz_hours = int(tz[1:3])
    tz_mins = int(tz[3:5])
    offset_seconds = tz_sign * (tz_hours * 3600 + tz_mins * 60)
    from datetime import timedelta
    naive = datetime(int(year), month, int(day), int(hour), int(minute), int(second))
    return (naive - timedelta(seconds=offset_seconds)).replace(tzinfo=timezone.utc)


def parse_line(line: str) -> Optional[LogEntry]:
    """Parse a single log line in Apache Combined Log Format.

    Returns None if the line doesn't match the expected format.
    """
    line = line.strip()
    if not line:
        return None
    m = LOG_LINE_RE.match(line)
    if not m:
        return None
    g = m.groupdict()
    try:
        timestamp = parse_timestamp(g["timestamp"])
    except ValueError:
        return None
    bytes_str = g["bytes"]
    bytes_val = 0 if bytes_str == "-" else int(bytes_str)
    return LogEntry(
        ip=g["ip"],
        user=g["user"],
        timestamp=timestamp,
        method=g["method"],
        url=g["url"],
        protocol=g["protocol"],
        status=int(g["status"]),
        bytes=bytes_val,
    )


def parse_lines(lines):
    """Parse an iterable of log lines, yielding LogEntry for each parseable line."""
    for line in lines:
        entry = parse_line(line)
        if entry is not None:
            yield entry
