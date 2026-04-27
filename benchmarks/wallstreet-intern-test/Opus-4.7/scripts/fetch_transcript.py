"""Fetch a transcript URL with a desktop User-Agent and save to raw/transcripts/.
Adds a timestamped row to sources.md with SHA-256 of the response body."""
from __future__ import annotations

import hashlib
import pathlib
import sys
import datetime as dt
import time

import requests

REPO = pathlib.Path(__file__).resolve().parent.parent
SOURCES_MD = REPO / "sources.md"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def _next_idx() -> int:
    text = SOURCES_MD.read_text(encoding="utf-8")
    n = 0
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cell = line.split("|")[1].strip()
        if cell.isdigit():
            n = max(n, int(cell))
    return n + 1


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: fetch_transcript.py <url> <out_filename> [note]")
        sys.exit(2)
    url = sys.argv[1]
    out_name = sys.argv[2]
    note = sys.argv[3] if len(sys.argv) > 3 else "Earnings call transcript"
    out_dir = REPO / "raw" / "transcripts"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / out_name
    headers = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}
    resp = requests.get(url, headers=headers, timeout=60)
    resp.raise_for_status()
    out_path.write_bytes(resp.content)
    sha = hashlib.sha256(resp.content).hexdigest()
    idx = _next_idx()
    ts = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M:%SZ")
    with SOURCES_MD.open("a", encoding="utf-8") as f:
        f.write(f"| {idx} | {ts} | {url} | `{sha}` | {note} |\n")
    print(f"OK {url} -> {out_path.relative_to(REPO).as_posix()} ({len(resp.content):,} bytes, sha {sha[:12]}...)")
    time.sleep(0.5)


if __name__ == "__main__":
    main()
