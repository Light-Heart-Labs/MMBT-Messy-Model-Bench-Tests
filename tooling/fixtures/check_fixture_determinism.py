#!/usr/bin/env python3
"""Determinism check for the frozen fixture mirror (protocol section 3 gate).

Fetches every fixture URL twice through a running serve_fixtures.py instance
and requires (a) both fetches byte-identical, (b) both matching the sha256
recorded in index.json, (c) the catalog pages themselves byte-stable.

Exit 0 = deterministic; exit 1 = any mismatch (protocol: p3_market is then
demoted to exploratory via DEVIATIONS.md).

Usage:
    python3 check_fixture_determinism.py [--base-url http://127.0.0.1:8377]
                                         [--root <fixture_root>]

python3 stdlib only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit


def fetch(base: str, path: str) -> bytes:
    with urllib.request.urlopen(base + path, timeout=30) as r:
        return r.read()


def mirror_path(url: str) -> str:
    sp = urlsplit(url)
    return "/" + sp.netloc + (sp.path if sp.path else "/")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:8377")
    ap.add_argument("--root", default=None)
    args = ap.parse_args()
    root = Path(args.root) if args.root else (
        Path(__file__).resolve().parent / "p3_market")
    index = json.loads((root / "index.json").read_text())
    base = args.base_url.rstrip("/")

    failures = 0
    checked = 0
    for fx in sorted(index["fixtures"], key=lambda r: r["url"]):
        path = mirror_path(fx["url"])
        try:
            b1 = fetch(base, path)
            b2 = fetch(base, path)
        except Exception as exc:
            print(f"FAIL fetch {path}: {exc}")
            failures += 1
            continue
        h1 = hashlib.sha256(b1).hexdigest()
        h2 = hashlib.sha256(b2).hexdigest()
        checked += 1
        if h1 != h2:
            print(f"FAIL nondeterministic {path}: {h1} != {h2}")
            failures += 1
        elif h1 != fx["sha256"]:
            print(f"FAIL corpus mismatch {path}: served {h1} != "
                  f"index {fx['sha256']}")
            failures += 1
        else:
            print(f"OK   {path} {h1[:16]} ({len(b1)} bytes x2)")

    for special in ("/", "/index.json"):
        try:
            b1, b2 = fetch(base, special), fetch(base, special)
        except Exception as exc:
            print(f"FAIL fetch {special}: {exc}")
            failures += 1
            continue
        checked += 1
        if b1 != b2:
            print(f"FAIL nondeterministic {special}")
            failures += 1
        else:
            print(f"OK   {special} ({len(b1)} bytes x2)")

    print(f"\nchecked={checked} failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
