from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
CIK = "0001670592"
UA = "Codex investment memo research contact codex@example.local"


@dataclass
class Source:
    source_id: str
    url: str
    local_path: str
    purpose: str


MANUAL_SOURCES: list[Source] = [
    Source(
        "YETI-IR-Q4-2025-PR",
        "https://investors.yeti.com/news/news-details/2026/YETI-ReportsFourth-Quarter-and-Full-Year-2025-Results-Provides-Full-Year-2026-Outlook/default.aspx",
        "raw/other/yeti-q4-fy2025-results-pr.html",
        "FY2025 results, FY2026 outlook, management commentary, non-GAAP reconciliations.",
    ),
    Source(
        "YETI-IR-Q3-2025-PR",
        "https://investors.yeti.com/news/news-details/2025/YETI-Reports-Third-Quarter-2025-Results/default.aspx",
        "raw/other/yeti-q3-2025-results-pr.html",
        "Q3 2025 results, repurchase update, management commentary.",
    ),
    Source(
        "YETI-IR-Q2-2025-PR",
        "https://investors.yeti.com/news/news-details/2025/YETI-Reports-Second-Quarter-2025-Results/default.aspx",
        "raw/other/yeti-q2-2025-results-pr.html",
        "Q2 2025 results and tariff commentary.",
    ),
    Source(
        "YETI-IR-Q1-2025-PR",
        "https://investors.yeti.com/news/news-details/2025/YETI-Reports-First-Quarter-2025-Results/default.aspx",
        "raw/other/yeti-q1-2025-results-pr.html",
        "Q1 2025 results and outlook baseline.",
    ),
    Source(
        "YETI-IR-Q4-2024-PR",
        "https://investors.yeti.com/news/news-details/2025/YETI-Reports-Fourth-Quarter-and-Fiscal-Year-2024-Results/default.aspx",
        "raw/other/yeti-q4-fy2024-results-pr.html",
        "FY2024 results and 2025 outlook comparison.",
    ),
    Source(
        "YETI-Q4-2025-TRANSCRIPT",
        "https://s22.q4cdn.com/322452763/files/doc_financials/2025/q4/YETI-4Q25-Earnings-Call-Transcript.pdf",
        "raw/transcripts/yeti-q4-2025-earnings-call-transcript.pdf",
        "Q4 2025 earnings-call transcript for management quotes.",
    ),
    Source(
        "YETI-Q3-2025-TRANSCRIPT",
        "https://s22.q4cdn.com/322452763/files/doc_financials/2025/q3/YETI-3Q25-Earnings-Call-Transcript.pdf",
        "raw/transcripts/yeti-q3-2025-earnings-call-transcript.pdf",
        "Q3 2025 earnings-call transcript for management quotes.",
    ),
    Source(
        "YETI-Q2-2025-TRANSCRIPT",
        "https://s22.q4cdn.com/322452763/files/doc_financials/2025/q2/YETI-Holdings-Inc-Q2-2025-Earnings-Call.pdf",
        "raw/transcripts/yeti-q2-2025-earnings-call-transcript.pdf",
        "Q2 2025 earnings-call transcript for management quotes.",
    ),
    Source(
        "YETI-Q1-2025-TRANSCRIPT",
        "https://s22.q4cdn.com/322452763/files/doc_financials/2025/q1/YETI-1Q25-Earnings-Transcript-050825.pdf",
        "raw/transcripts/yeti-q1-2025-earnings-call-transcript.pdf",
        "Q1 2025 earnings-call transcript for management quotes.",
    ),
    Source(
        "YETI-Q4-2024-TRANSCRIPT",
        "https://s22.q4cdn.com/322452763/files/doc_financials/2024/q4/YETI-4Q24-Earnings-Transcript.pdf",
        "raw/transcripts/yeti-q4-2024-earnings-call-transcript.pdf",
        "Q4 2024 earnings-call transcript for prior outlook comparison.",
    ),
    Source(
        "YETI-2026-PROXY",
        "https://s22.q4cdn.com/322452763/files/doc_financials/2025/ar/YETI-2026-Proxy-Statement.pdf",
        "raw/other/yeti-2026-proxy-statement.pdf",
        "Board, compensation, adjusted financial highlights, and ownership context.",
    ),
    Source(
        "STOCKANALYSIS-YETI-MARKET-CAP",
        "https://stockanalysis.com/stocks/yeti/market-cap/",
        "raw/other/stockanalysis-yeti-market-cap.html",
        "Market capitalization screen for company eligibility.",
    ),
    Source(
        "STOCKANALYSIS-YETI-FORECAST",
        "https://stockanalysis.com/stocks/yeti/forecast/",
        "raw/other/stockanalysis-yeti-forecast.html",
        "Public consensus price target and analyst rating snapshot.",
    ),
    Source(
        "STOCKANALYSIS-YETI-STATISTICS",
        "https://stockanalysis.com/stocks/yeti/statistics/",
        "raw/other/stockanalysis-yeti-statistics.html",
        "Market-data cross-check for valuation inputs.",
    ),
    Source(
        "STOCKANALYSIS-GOLF-STATISTICS",
        "https://stockanalysis.com/stocks/golf/statistics/",
        "raw/other/stockanalysis-golf-statistics.html",
        "Acushnet peer valuation and operating metrics.",
    ),
    Source(
        "STOCKANALYSIS-MAT-STATISTICS",
        "https://stockanalysis.com/stocks/mat/statistics/",
        "raw/other/stockanalysis-mat-statistics.html",
        "Mattel peer valuation and operating metrics.",
    ),
    Source(
        "STOCKANALYSIS-NWL-STATISTICS",
        "https://stockanalysis.com/stocks/nwl/statistics/",
        "raw/other/stockanalysis-nwl-statistics.html",
        "Newell Brands peer valuation and operating metrics.",
    ),
    Source(
        "STOCKANALYSIS-DTC-STATISTICS",
        "https://stockanalysis.com/stocks/dtc/statistics/",
        "raw/other/stockanalysis-dtc-statistics.html",
        "Solo Brands peer valuation and operating metrics.",
    ),
    Source(
        "SEC-SUBMISSIONS-YETI",
        f"https://data.sec.gov/submissions/CIK{CIK}.json",
        "raw/filings/sec-submissions-CIK0001670592.json",
        "SEC submissions index used to locate filings.",
    ),
    Source(
        "SEC-COMPANYFACTS-YETI",
        f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json",
        "raw/filings/sec-companyfacts-CIK0001670592.json",
        "XBRL company facts used for extraction cross-checks.",
    ),
    Source(
        "US-TREASURY-DAILY-RATES",
        "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2026",
        "raw/other/us-treasury-daily-yield-curve-2026.html",
        "Risk-free-rate input for cost of equity/WACC.",
    ),
    Source(
        "KROLL-ERP-2026",
        "https://www.kroll.com/en/insights/publications/cost-of-capital/recommended-us-equity-risk-premium-and-corresponding-risk-free-rates",
        "raw/other/kroll-us-equity-risk-premium.html",
        "Equity risk premium input for cost of equity.",
    ),
]


def fetch(url: str) -> tuple[bytes, str]:
    request = Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
    with urlopen(request, timeout=60) as response:
        final_url = response.geturl()
        return response.read(), final_url


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_file(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def source_row(source_id: str, timestamp: str, url: str, local_path: str, digest: str, purpose: str) -> str:
    safe_purpose = purpose.replace("\n", " ").replace("|", "\\|")
    return f"| {source_id} | {timestamp} | {url} | `{local_path}` | `{digest}` | {safe_purpose} |\n"


def download_source(source: Source) -> dict:
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    data, final_url = fetch(source.url)
    digest = sha256(data)
    local_path = ROOT / source.local_path
    write_file(local_path, data)
    return {
        "source_id": source.source_id,
        "timestamp_utc": timestamp,
        "url": final_url,
        "local_path": source.local_path,
        "sha256": digest,
        "purpose": source.purpose,
        "bytes": len(data),
    }


def locate_sec_filings() -> list[Source]:
    submissions_path = ROOT / "raw/filings/sec-submissions-CIK0001670592.json"
    if not submissions_path.exists():
        raise FileNotFoundError("SEC submissions JSON must be downloaded before locating filings")
    submissions = json.loads(submissions_path.read_text(encoding="utf-8"))
    recent = submissions["filings"]["recent"]
    filings: list[Source] = []
    targets = {
        "10-K": 3,
        "10-Q": 3,
        "8-K": 4,
    }
    counts = {key: 0 for key in targets}
    for idx, form in enumerate(recent["form"]):
        if form not in targets or counts[form] >= targets[form]:
            continue
        accession = recent["accessionNumber"][idx]
        primary_doc = recent["primaryDocument"][idx]
        filing_date = recent["filingDate"][idx]
        accession_nodash = accession.replace("-", "")
        url = f"https://www.sec.gov/Archives/edgar/data/{int(CIK)}/{accession_nodash}/{primary_doc}"
        slug = primary_doc.lower().replace("/", "-")
        local = f"raw/filings/yeti-{filing_date}-{form.lower().replace('/', '')}-{slug}"
        filings.append(
            Source(
                f"SEC-YETI-{form}-{filing_date}-{counts[form] + 1}",
                url,
                local,
                f"YETI {form} filed {filing_date}; original SEC primary document.",
            )
        )
        counts[form] += 1
    return filings


def refresh_sources_md(records: Iterable[dict]) -> None:
    header = (
        "# Sources\n\n"
        "Every fetched external URL is recorded here with UTC timestamp, local path, SHA-256, and purpose.\n\n"
        "| ID | Timestamp UTC | URL | Local path | SHA-256 | Purpose |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
    )
    rows = [
        source_row(
            record["source_id"],
            record["timestamp_utc"],
            record["url"],
            record["local_path"],
            record["sha256"],
            record["purpose"],
        )
        for record in records
    ]
    (ROOT / "sources.md").write_text(header + "".join(rows), encoding="utf-8")


def main() -> int:
    records: list[dict] = []
    errors: list[tuple[Source, str]] = []
    for source in MANUAL_SOURCES:
        try:
            record = download_source(source)
            records.append(record)
            print(f"OK {record['source_id']} {record['bytes']} bytes")
            time.sleep(0.2)
        except HTTPError as exc:
            errors.append((source, f"HTTP {exc.code}"))
            print(f"MISS {source.source_id}: HTTP {exc.code}", file=sys.stderr)
        except Exception as exc:  # noqa: BLE001
            errors.append((source, repr(exc)))
            print(f"MISS {source.source_id}: {exc!r}", file=sys.stderr)

    for source in locate_sec_filings():
        try:
            record = download_source(source)
            records.append(record)
            print(f"OK {record['source_id']} {record['bytes']} bytes")
            time.sleep(0.2)
        except Exception as exc:  # noqa: BLE001
            errors.append((source, repr(exc)))
            print(f"MISS {source.source_id}: {exc!r}", file=sys.stderr)

    refresh_sources_md(records)
    (ROOT / "raw/source-download-errors.json").write_text(
        json.dumps(
            [
                {
                    "source_id": source.source_id,
                    "url": source.url,
                    "local_path": source.local_path,
                    "error": error,
                }
                for source, error in errors
            ],
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Downloaded {len(records)} sources; {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
