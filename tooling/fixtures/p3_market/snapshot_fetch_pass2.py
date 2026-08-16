#!/usr/bin/env python3
"""Second-pass fetcher: snapshot substitute URLs for targets that failed in
pass 1 and merge them into tooling/fixtures/p3_market/index.json."""
from __future__ import annotations

import datetime
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path("/home/michael/mmbt-qwen38-eaaa8ca")
ROOT = REPO / "tooling" / "fixtures" / "p3_market"
PAGES = ROOT / "pages"

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

URLS = [
    "https://support.1password.com/sso/",
    "https://bitwarden.com/products/business/",
    "https://www.keepersecurity.com/security.html",
    "https://www.keepersecurity.com/business.html",
    "https://nordpass.com/plans/",
    "https://developer.hashicorp.com/vault",
]


def slug_for(url: str) -> str:
    s = re.sub(r"^https?://", "", url)
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("_")
    return s[:140] + ".html"


def utcnow() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    index = json.loads((ROOT / "index.json").read_text())
    have = {f["url"] for f in index["fixtures"]}
    for url in URLS:
        if url in have:
            print(f"SKIP already present {url}")
            continue
        slug = slug_for(url)
        out = PAGES / slug
        t0 = utcnow()
        cmd = [
            "curl", "-sS", "-L", "--compressed",
            "--max-time", "75", "--retry", "2", "--retry-delay", "2",
            "-A", UA,
            "-H", "Accept: text/html,application/xhtml+xml,application/xml;"
                  "q=0.9,image/avif,image/webp,*/*;q=0.8",
            "-H", "Accept-Language: en-US,en;q=0.9",
            "-o", str(out),
            "-w", "%{http_code}\t%{content_type}\t%{url_effective}",
            url,
        ]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        parts = (p.stdout.strip().split("\t") + ["", "", ""])[:3]
        code, ctype, final_url = parts[0], parts[1], parts[2]
        size = out.stat().st_size if out.exists() else 0
        if p.returncode == 0 and code == "200" and size > 0:
            index["fixtures"].append({
                "url": url,
                "final_url": final_url,
                "path": f"pages/{slug}",
                "http_status": int(code),
                "content_type": ctype or "text/html",
                "fetch_time_utc": t0,
                "sha256": sha256_file(out),
                "bytes": size,
            })
            print(f"OK   {code} {size:>9} {url}")
        else:
            if out.exists():
                out.unlink()
            index["unfetchable"].append({
                "url": url,
                "http_status": int(code) if code.isdigit() else None,
                "curl_exit": p.returncode,
                "error": (p.stderr.strip() or f"http {code}")[:300],
                "fetch_time_utc": t0,
            })
            print(f"FAIL {code or '---'} curl={p.returncode} {url}")
        time.sleep(2)

    index["fixtures"] = sorted(index["fixtures"], key=lambda r: r["url"])
    index["unfetchable"] = sorted(index["unfetchable"], key=lambda r: r["url"])
    index["created_utc"] = utcnow()
    (ROOT / "index.json").write_text(
        json.dumps(index, indent=2, sort_keys=True) + "\n")
    print(f"\nfixtures: {len(index['fixtures'])}  "
          f"unfetchable: {len(index['unfetchable'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
