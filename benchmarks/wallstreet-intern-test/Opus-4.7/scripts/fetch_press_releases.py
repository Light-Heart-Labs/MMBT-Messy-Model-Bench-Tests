"""For each earnings 8-K, fetch its filing-index, find the Ex. 99.1 press release,
and download it into raw/filings/ with a clean name."""
from __future__ import annotations

import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fetch_edgar import fetch  # noqa: E402

CIK = 1482981
REPO = pathlib.Path(__file__).resolve().parent.parent

EARNINGS_8K = [
    ("Q4-FY2025", "2026-02-18", "0001482981-26-000019"),
    ("Q3-2025",   "2025-10-29", "0001628280-25-046919"),
    ("Q2-2025",   "2025-07-30", "0001482981-25-000129"),
    ("Q1-2025",   "2025-04-30", "0001482981-25-000080"),
    ("Q4-FY2024", "2025-02-26", "0001482981-25-000028"),
    ("Q3-2024",   "2024-10-30", "0001482981-24-000125"),
    ("Q2-2024",   "2024-07-31", "0001482981-24-000098"),
    ("Q1-2024",   "2024-05-01", "0001482981-24-000060"),
    ("Q4-FY2023", "2024-02-28", "0001482981-24-000008"),
]


def main() -> None:
    out_dir = REPO / "raw" / "filings"
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = REPO / "raw" / "other"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    for label, fdate, accession in EARNINGS_8K:
        idx_url = f"https://www.sec.gov/Archives/edgar/data/{CIK}/{accession.replace('-', '')}/"
        idx_path = tmp_dir / f"index_{accession}.html"
        if not idx_path.exists():
            fetch(idx_url, idx_path, note=f"Index for {label} 8-K")
        text = idx_path.read_text(encoding="utf-8", errors="ignore")
        # find file references that look like a press release exhibit (skip the cover doc)
        candidates = re.findall(r'href="(/Archives/edgar/data/\d+/\d+/[^"]+\.htm)"', text)
        # filter to filenames containing 'ex' or 'press' or '991', exclude R*.htm summary files
        pr_url = None
        for c in candidates:
            fn = c.rsplit("/", 1)[-1].lower()
            if re.match(r'^r\d+\.htm$', fn):
                continue
            if any(tag in fn for tag in ("99", "press", "ex991", "exx991")):
                pr_url = "https://www.sec.gov" + c
                break
        if not pr_url:
            print(f"!!! could not locate press release for {label} accession {accession}")
            continue
        out_name = f"PR_{label}_{accession.split('-', 1)[1]}.htm"
        out_path = out_dir / out_name
        if out_path.exists():
            print(f"skip {out_path.name}")
            continue
        fetch(pr_url, out_path, note=f"{label} press release (8-K Ex. 99.1)")


if __name__ == "__main__":
    main()
