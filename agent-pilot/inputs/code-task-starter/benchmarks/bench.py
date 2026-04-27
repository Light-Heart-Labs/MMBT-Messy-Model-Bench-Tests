"""Performance benchmark — times log loading on a synthetic large file.

Generates a 50 MB synthetic access log if not already present, then times how long
it takes to load and parse with `logalyzer.io.load`. Prints wall time in seconds
and entries/sec. Designed to be run before and after changes to compare speedups.

Usage:
    python benchmarks/bench.py [--size MB]
"""
from __future__ import annotations

import argparse
import os
import random
import sys
import time
from pathlib import Path

# Make logalyzer importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from logalyzer.io import load


SAMPLE_LINE_TEMPLATE = (
    '{ip} - - [{day:02d}/{month}/2026:{h:02d}:{m:02d}:{s:02d} +0000] '
    '"{method} {url} HTTP/1.1" {status} {bytes}\n'
)


def generate_log(path: Path, target_mb: int = 50) -> None:
    """Generate a synthetic log file approximately `target_mb` megabytes in size."""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    methods = ["GET", "POST", "PUT", "DELETE"]
    urls = ["/", "/api/users", "/api/orders", "/static/app.js", "/admin/login",
            "/health", "/metrics", "/products/123", "/search?q=foo", "/checkout"]
    statuses = [200, 200, 200, 200, 301, 404, 500]
    rng = random.Random(42)

    target_bytes = target_mb * 1024 * 1024
    written = 0
    with open(path, "w") as f:
        while written < target_bytes:
            line = SAMPLE_LINE_TEMPLATE.format(
                ip=f"{rng.randint(1, 254)}.{rng.randint(0, 254)}.{rng.randint(0, 254)}.{rng.randint(1, 254)}",
                day=rng.randint(1, 28),
                month=rng.choice(months),
                h=rng.randint(0, 23),
                m=rng.randint(0, 59),
                s=rng.randint(0, 59),
                method=rng.choice(methods),
                url=rng.choice(urls),
                status=rng.choice(statuses),
                bytes=rng.randint(100, 50000),
            )
            f.write(line)
            written += len(line)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=50, help="target log size in MB")
    ap.add_argument("--keep", action="store_true", help="don't regenerate if file exists")
    args = ap.parse_args()

    bench_dir = Path(__file__).resolve().parent
    log_path = bench_dir / f"bench_{args.size}mb.log"

    if not log_path.exists() or not args.keep:
        print(f"Generating {args.size} MB log at {log_path}…", file=sys.stderr)
        generate_log(log_path, args.size)

    actual_size_mb = os.path.getsize(log_path) / (1024 * 1024)
    print(f"log size: {actual_size_mb:.1f} MB", file=sys.stderr)

    print("loading…", file=sys.stderr)
    t0 = time.perf_counter()
    entries = load(str(log_path))
    elapsed = time.perf_counter() - t0
    eps = len(entries) / elapsed if elapsed > 0 else 0

    print(f"entries:  {len(entries)}")
    print(f"elapsed:  {elapsed:.3f} s")
    print(f"eps:      {eps:.0f} entries/sec")
    print(f"mb_per_s: {actual_size_mb/elapsed:.2f}")


if __name__ == "__main__":
    main()
