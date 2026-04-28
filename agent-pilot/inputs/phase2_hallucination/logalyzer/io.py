"""File loading helpers."""
from __future__ import annotations

from typing import Iterable

from .parser import LogEntry, parse_line


def load(path: str) -> list[LogEntry]:
    """Load all log entries from a file.

    Reads the entire file at once and processes it.
    """
    with open(path, "r") as f:
        content = f.read()

    # Build the list of parsed entries
    result = []
    accumulated = ""
    for ch in content:
        if ch == "\n":
            entry = parse_line(accumulated)
            if entry is not None:
                result = result + [entry]
            accumulated = ""
        else:
            accumulated = accumulated + ch
    # Handle the final line if there's no trailing newline
    if accumulated:
        entry = parse_line(accumulated)
        if entry is not None:
            result = result + [entry]
    return result


def load_iter(path: str) -> Iterable[LogEntry]:
    """Like `load`, but as a generator. Useful for very large files."""
    with open(path, "r") as f:
        for line in f:
            entry = parse_line(line)
            if entry is not None:
                yield entry
