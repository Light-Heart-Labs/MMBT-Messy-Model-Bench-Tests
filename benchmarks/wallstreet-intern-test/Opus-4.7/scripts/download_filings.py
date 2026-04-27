"""Download a curated set of SEC filings into raw/filings/.

Reads a manifest list defined inline (CIK 1482981 = Vita Coco) and pulls each
filing's primary document plus the filing-index page (so the full set of
exhibits is referenceable later).

Naming convention: raw/filings/<form>_<reportdate>_<accession>.htm
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fetch_edgar import fetch  # noqa: E402

CIK = 1482981
REPO = pathlib.Path(__file__).resolve().parent.parent

# (form, filing_date, report_date, accession, primary_doc, label)
MANIFEST = [
    # Annual reports - 5 fiscal years
    ("10-K", "2026-02-18", "2025-12-31", "0001482981-26-000022", "coco-20251231.htm", "FY2025 annual report"),
    ("10-K", "2025-02-26", "2024-12-31", "0001482981-25-000032", "coco-20241231.htm", "FY2024 annual report"),
    ("10-K", "2024-02-29", "2023-12-31", "0001482981-24-000012", "coco-20231231.htm", "FY2023 annual report"),
    ("10-K", "2023-03-14", "2022-12-31", "0001482981-23-000017", "coco-20221231.htm", "FY2022 annual report"),
    ("10-K", "2022-03-14", "2021-12-31", "0001482981-22-000014", "coco-20211231.htm", "FY2021 annual report"),
    # Most recent quarters
    ("10-Q", "2025-10-29", "2025-09-30", "0001628280-25-046935", "coco-20250930.htm", "Q3 2025"),
    ("10-Q", "2025-07-30", "2025-06-30", "0001482981-25-000133", "coco-20250630.htm", "Q2 2025"),
    ("10-Q", "2025-04-30", "2025-03-31", "0001482981-25-000082", "coco-20250331.htm", "Q1 2025"),
    # Earnings press releases (8-Ks containing tables)
    ("8-K", "2026-02-18", "2026-02-18", "0001482981-26-000019", "coco-20260218.htm", "Q4/FY 2025 earnings release"),
    ("8-K", "2025-10-29", "2025-10-29", "0001628280-25-046919", "coco-20250930x8k.htm", "Q3 2025 earnings release"),
    ("8-K", "2025-07-30", "2025-07-30", "0001482981-25-000129", "coco-20250730.htm", "Q2 2025 earnings release"),
    ("8-K", "2025-04-30", "2025-04-30", "0001482981-25-000080", "coco-20250430.htm", "Q1 2025 earnings release"),
    ("8-K", "2025-02-26", "2025-02-26", "0001482981-25-000028", "coco-20250226.htm", "Q4/FY 2024 earnings release"),
    # Most recent proxy
    ("DEF14A", "2026-04-22", "2025-12-31", "0001482981-26-000107", "coco-20260422.htm", "2026 proxy"),
]


def acc_path(accession: str) -> str:
    return accession.replace("-", "")


def base_url(accession: str) -> str:
    return f"https://www.sec.gov/Archives/edgar/data/{CIK}/{acc_path(accession)}"


def main() -> None:
    out_dir = REPO / "raw" / "filings"
    out_dir.mkdir(parents=True, exist_ok=True)

    for form, fdate, rdate, accession, primary, label in MANIFEST:
        # primary doc
        url = f"{base_url(accession)}/{primary}"
        # use a clean filename: form, report date, accession-tail
        acc_tail = accession.split("-", 1)[1]
        safe_form = form.replace("/", "_")
        out_name = f"{safe_form}_{rdate or fdate}_{acc_tail}.htm"
        out_path = out_dir / out_name
        if out_path.exists():
            print(f"skip {out_path.name} (exists)")
            continue
        fetch(url, out_path, note=f"{form} {label}")


if __name__ == "__main__":
    main()
