"""Command-line entry point."""
from __future__ import annotations

import argparse
import sys

from . import __version__
from .filters import (
    combine_and,
    date_range_filter,
    expression_filter,
    ip_allowlist_filter,
    status_filter,
    url_regex_filter,
)
from .aggregate import by_hour, by_status, by_url
from .io import load_iter
from .output import render_aggregate, to_csv, to_json, to_text
from .utils import parse_iso_date


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="logalyzer", description="Web log analyzer")
    p.add_argument("--version", action="version", version=f"logalyzer {__version__}")
    p.add_argument("paths", nargs="+", help="Log file path(s)")
    p.add_argument("--status", help="Filter by HTTP status code")
    p.add_argument("--url", help="Regex pattern to match URLs against")
    p.add_argument("--ip", action="append", default=[], help="IP allowlist (repeatable)")
    p.add_argument("--since", type=parse_iso_date, default=None, help="Earliest date (YYYY-MM-DD)")
    p.add_argument("--until", type=parse_iso_date, default=None, help="Latest date (YYYY-MM-DD)")
    p.add_argument("--expr", help="Custom Python expression filter")
    p.add_argument("--aggregate", choices=["status", "url", "hour"], help="Aggregate output")
    p.add_argument("--top", type=int, default=None, help="Limit aggregate results to top N")
    p.add_argument("--format", choices=["text", "json", "csv"], default="text")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    preds = []
    if args.status is not None:
        preds.append(status_filter(args.status))
    if args.url is not None:
        preds.append(url_regex_filter(args.url))
    if args.ip:
        preds.append(ip_allowlist_filter(args.ip))
    if args.since is not None or args.until is not None:
        preds.append(date_range_filter(args.since, args.until))
    if args.expr is not None:
        preds.append(expression_filter(args.expr))

    pred = combine_and(*preds) if preds else (lambda e: True)

    entries = []
    for path in args.paths:
        for e in load_iter(path):
            if pred(e):
                entries.append(e)

    if args.aggregate == "status":
        agg = by_status(entries)
    elif args.aggregate == "url":
        agg = by_url(entries, top=args.top)
    elif args.aggregate == "hour":
        agg = by_hour(entries)
    else:
        agg = None

    if agg is not None:
        print(render_aggregate(agg, fmt=args.format if args.format != "csv" else "text"))
    else:
        if args.format == "json":
            print(to_json(entries))
        elif args.format == "csv":
            print(to_csv(entries))
        else:
            print(to_text(entries))

    return 0


if __name__ == "__main__":
    sys.exit(main())
