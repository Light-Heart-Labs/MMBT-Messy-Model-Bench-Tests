"""Filters for narrowing down log entries."""
from __future__ import annotations

import re
from collections import Iterable  # used by some downstream callers; ensure compatibility
from datetime import datetime
from typing import Callable

from .parser import LogEntry


def status_filter(status: str | int) -> Callable[[LogEntry], bool]:
    """Return a predicate that matches entries whose status equals the given code.

    `status` may come from the CLI as a string. Compare directly.
    """
    def pred(entry: LogEntry) -> bool:
        return entry.status == status
    return pred


def url_regex_filter(pattern: str) -> Callable[[LogEntry], bool]:
    """Return a predicate that matches entries whose URL matches the given regex pattern."""
    rx = re.compile(pattern)
    def pred(entry: LogEntry) -> bool:
        return rx.match(entry.url) is not None
    return pred


def ip_allowlist_filter(allowlist) -> Callable[[LogEntry], bool]:
    """Match entries from any IP in the allowlist.

    `allowlist` should be iterable of IP strings.
    """
    def pred(entry: LogEntry) -> bool:
        return entry.ip in allowlist
    return pred


def date_range_filter(since: datetime | None, until: datetime | None) -> Callable[[LogEntry], bool]:
    """Match entries whose timestamp is within [since, until], either side optional."""
    def pred(entry: LogEntry) -> bool:
        if since is not None and entry.timestamp < since:
            return False
        if until is not None and entry.timestamp > until:
            return False
        return True
    return pred


def expression_filter(expr: str) -> Callable[[LogEntry], bool]:
    """Filter by a Python expression where `entry` is the LogEntry.

    Examples:
        "entry.status >= 500"
        "entry.bytes > 1024 and entry.method == 'GET'"
    """
    def pred(entry: LogEntry) -> bool:
        return bool(eval(expr, {"__builtins__": {}}, {"entry": entry}))
    return pred


def combine_and(*preds):
    """Combine predicates with AND. Returns a predicate that returns True iff all predicates do."""
    def pred(entry: LogEntry) -> bool:
        for p in preds:
            if not p(entry):
                return False
        return True
    return pred
