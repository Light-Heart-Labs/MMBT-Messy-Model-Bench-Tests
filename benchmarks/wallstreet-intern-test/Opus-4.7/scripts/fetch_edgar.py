"""Fetch SEC EDGAR resources with the required User-Agent header.

Usage:
    python fetch_edgar.py <url> <output_path>
    python fetch_edgar.py submissions <cik>           # writes raw/other/edgar_submissions_<cik>.json
    python fetch_edgar.py companyfacts <cik>          # writes raw/other/edgar_companyfacts_<cik>.json

After every fetch, append a row to ../sources.md with timestamp + SHA-256.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import os
import pathlib
import sys
import time

import requests

# SEC EDGAR fair-access policy: identify yourself + cap to ~10 req/s.
HEADERS = {
    "User-Agent": "Investment Memo Research claude-research@example.com",
    "Accept-Encoding": "gzip, deflate",
    "Host": None,  # set per request
}

REPO = pathlib.Path(__file__).resolve().parent.parent
SOURCES_MD = REPO / "sources.md"


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _next_source_index() -> int:
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


def _append_source(url: str, sha: str, note: str) -> None:
    idx = _next_source_index()
    ts = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
    line = f"| {idx} | {ts} | {url} | `{sha}` | {note} |\n"
    with SOURCES_MD.open("a", encoding="utf-8") as f:
        f.write(line)


def fetch(url: str, out_path: pathlib.Path, note: str = "", sleep_s: float = 0.2) -> str:
    headers = {k: v for k, v in HEADERS.items() if v is not None}
    resp = requests.get(url, headers=headers, timeout=60)
    resp.raise_for_status()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(resp.content)
    sha = _sha256(resp.content)
    _append_source(url, sha, note or out_path.relative_to(REPO).as_posix())
    print(f"OK  {url} -> {out_path.relative_to(REPO).as_posix()}  ({len(resp.content):,} bytes, sha {sha[:12]}...)")
    time.sleep(sleep_s)
    return sha


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)

    cmd = sys.argv[1]
    if cmd == "submissions":
        cik = sys.argv[2].zfill(10)
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        out = REPO / "raw" / "other" / f"edgar_submissions_{cik}.json"
        fetch(url, out, note=f"EDGAR submissions index for CIK {cik}")
    elif cmd == "companyfacts":
        cik = sys.argv[2].zfill(10)
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        out = REPO / "raw" / "other" / f"edgar_companyfacts_{cik}.json"
        fetch(url, out, note=f"EDGAR companyfacts (XBRL) for CIK {cik}")
    else:
        url = sys.argv[1]
        out = pathlib.Path(sys.argv[2])
        if not out.is_absolute():
            out = REPO / out
        note = sys.argv[3] if len(sys.argv) > 3 else ""
        fetch(url, out, note=note)


if __name__ == "__main__":
    main()
