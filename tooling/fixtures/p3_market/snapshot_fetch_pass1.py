#!/usr/bin/env python3
"""One-shot snapshot fetcher for the p3_market offline fixture corpus.

Fetches every target URL with curl, stores the decoded response body under
tooling/fixtures/p3_market/pages/, and writes index.json with per-fixture
url, fetch time, sha256, and byte size. Non-200 targets are recorded in the
"unfetchable" list and no body file is kept for them.

Run once on tower2 from the repo root checkout. python3 stdlib + curl only.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/home/michael/mmbt-qwen38-eaaa8ca")
ROOT = REPO / "tooling" / "fixtures" / "p3_market"
PAGES = ROOT / "pages"

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# Target list. Sources of truth:
#  - tooling/graders/ground_truth/phase3_market_research_rubric.json
#    products_in_scope: 1Password, Bitwarden, Dashlane, Keeper, LastPass,
#    Vault (category-distinguish only)
#  - empirical URL-frequency extraction from the prior campaign's
#    logs/p3_market_*/transcript.jsonl (agents also relied on Proton Pass and
#    NordPass, plus Wikipedia for incident history)
URLS = [
    # 1Password
    "https://1password.com/pricing/",
    "https://1password.com/pricing/business",
    "https://1password.com/business/",
    "https://1password.com/security/",
    "https://1password.com/trust/",
    "https://support.1password.com/advanced-features/sso/",
    # Bitwarden
    "https://bitwarden.com/pricing/",
    "https://bitwarden.com/pricing/business/",
    "https://bitwarden.com/compliance/",
    "https://bitwarden.com/security/",
    "https://bitwarden.com/business/",
    "https://bitwarden.com/help/about-sso/",
    "https://bitwarden.com/help/event-logs/",
    "https://bitwarden.com/help/is-bitwarden-audited/",
    # Dashlane
    "https://www.dashlane.com/pricing",
    "https://www.dashlane.com/en-us/pricing/password-management",
    "https://www.dashlane.com/business-password-manager",
    "https://www.dashlane.com/security",
    # LastPass
    "https://www.lastpass.com/pricing",
    "https://www.lastpass.com/security",
    "https://www.lastpass.com/trust-center/compliance",
    "https://compliance.lastpass.com/",
    "https://blog.lastpass.com/posts/notice-of-recent-security-incident",
    "https://blog.lastpass.com/2022/12/notice-of-recent-security-incident/",
    # Keeper
    "https://www.keeper.com/pricing",
    "https://www.keepersecurity.com/pricing.html",
    "https://www.keeper.com/security",
    # Proton Pass
    "https://proton.me/business/pass",
    "https://proton.me/pass/pricing",
    "https://proton.me/business/trust",
    # NordPass
    "https://www.nordpass.com/pricing",
    "https://www.nordpass.com/business",
    # Wikipedia background / incident history
    "https://en.wikipedia.org/wiki/1Password",
    "https://en.wikipedia.org/wiki/Bitwarden",
    "https://en.wikipedia.org/wiki/Dashlane",
    "https://en.wikipedia.org/wiki/LastPass",
    "https://en.wikipedia.org/wiki/Keeper_(password_manager)",
    "https://en.wikipedia.org/wiki/Proton_Pass",
    "https://en.wikipedia.org/wiki/NordPass",
    # Category distinguisher (secrets management, NOT a password manager)
    "https://www.hashicorp.com/products/vault",
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
    PAGES.mkdir(parents=True, exist_ok=True)
    fixtures = []
    unfetchable = []
    slugs_seen = {}

    for url in URLS:
        slug = slug_for(url)
        if slug in slugs_seen:
            print(f"FATAL slug collision: {url} vs {slugs_seen[slug]}")
            return 2
        slugs_seen[slug] = url
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
        ok = p.returncode == 0 and code == "200" and size > 0
        if ok:
            digest = sha256_file(out)
            fixtures.append({
                "url": url,
                "final_url": final_url,
                "path": f"pages/{slug}",
                "http_status": int(code),
                "content_type": ctype or "text/html",
                "fetch_time_utc": t0,
                "sha256": digest,
                "bytes": size,
            })
            print(f"OK   {code} {size:>9} {url}")
        else:
            if out.exists():
                out.unlink()
            unfetchable.append({
                "url": url,
                "http_status": int(code) if code.isdigit() else None,
                "curl_exit": p.returncode,
                "error": (p.stderr.strip() or f"http {code}")[:300],
                "fetch_time_utc": t0,
            })
            print(f"FAIL {code or '---'} curl={p.returncode} {url}")

    index = {
        "schema_version": 1,
        "task_family": "p3_market",
        "description": (
            "Frozen offline snapshot corpus for the p3_market task family. "
            "Served deterministically by tooling/fixtures/serve_fixtures.py; "
            "agents must cite the original url of each snapshot."),
        "created_utc": utcnow(),
        "fetch_host": "tower2",
        "fetch_tool": ("curl -sS -L --compressed --max-time 75 --retry 2 "
                       "-A <user_agent>"),
        "user_agent": UA,
        "fixtures": sorted(fixtures, key=lambda r: r["url"]),
        "unfetchable": sorted(unfetchable, key=lambda r: r["url"]),
    }
    (ROOT / "index.json").write_text(
        json.dumps(index, indent=2, sort_keys=True) + "\n")
    print(f"\nfixtures: {len(fixtures)}  unfetchable: {len(unfetchable)}")
    print(f"index: {ROOT / 'index.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
