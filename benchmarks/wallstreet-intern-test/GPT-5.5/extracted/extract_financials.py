from __future__ import annotations

import csv
import json
import re
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
OUT = ROOT / "extracted"
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)


FISCAL_YEARS = [2023, 2024, 2025]

ANNUAL_TAGS = {
    "revenue": ("RevenueFromContractWithCustomerExcludingAssessedTax", "USD"),
    "cogs": ("CostOfRevenue", "USD"),
    "gross_profit": ("GrossProfit", "USD"),
    "sga": ("SellingGeneralAndAdministrativeExpense", "USD"),
    "operating_income": ("OperatingIncomeLoss", "USD"),
    "pretax_income": (
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
        "USD",
    ),
    "income_tax": ("IncomeTaxExpenseBenefit", "USD"),
    "net_income": ("NetIncomeLoss", "USD"),
    "diluted_eps": ("EarningsPerShareDiluted", "USD/shares"),
    "diluted_shares": ("WeightedAverageNumberOfDilutedSharesOutstanding", "shares"),
    "operating_cash_flow": ("NetCashProvidedByUsedInOperatingActivities", "USD"),
    "capex": ("PaymentsToAcquirePropertyPlantAndEquipment", "USD"),
    "depreciation_amortization": ("DepreciationDepletionAndAmortization", "USD"),
    "stock_comp": ("ShareBasedCompensation", "USD"),
    "share_repurchases": ("PaymentsForRepurchaseOfCommonStock", "USD"),
}

INSTANT_TAGS = {
    "cash": ("CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", "USD"),
    "accounts_receivable": ("AccountsReceivableNetCurrent", "USD"),
    "inventory": ("InventoryNet", "USD"),
    "prepaids_other_current_assets": ("PrepaidExpenseAndOtherAssetsCurrent", "USD"),
    "current_assets": ("AssetsCurrent", "USD"),
    "ppe_net": ("PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization", "USD"),
    "operating_lease_assets": ("OperatingLeaseRightOfUseAsset", "USD"),
    "goodwill": ("Goodwill", "USD"),
    "intangible_assets": ("IntangibleAssetsNetExcludingGoodwill", "USD"),
    "total_assets": ("Assets", "USD"),
    "accounts_payable": ("AccountsPayableCurrent", "USD"),
    "accrued_expenses": ("AccruedLiabilitiesCurrent", "USD"),
    "current_liabilities": ("LiabilitiesCurrent", "USD"),
    "current_debt": ("LongTermDebtCurrent", "USD"),
    "long_term_debt": ("LongTermDebtNoncurrent", "USD"),
    "operating_lease_liabilities": ("OperatingLeaseLiability", "USD"),
    "total_liabilities": ("Liabilities", "USD"),
    "stockholders_equity": ("StockholdersEquity", "USD"),
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def clean_number(value: str) -> float:
    value = value.replace(",", "").replace("$", "").strip()
    if value in {"", "N/A", "n/a", "null"}:
        raise ValueError(f"not a number: {value!r}")
    return float(value)


def parse_money_string(value: str) -> float:
    value = value.replace(",", "").replace("$", "").strip()
    match = re.fullmatch(r"(-?\d+(?:\.\d+)?)([BMK]?)", value, flags=re.I)
    if not match:
        return clean_number(value)
    number = float(match.group(1))
    suffix = match.group(2).upper()
    scale = {"": 1, "K": 1_000, "M": 1_000_000, "B": 1_000_000_000}[suffix]
    return number * scale


def accession_source_map() -> dict[str, str]:
    submissions = read_json(RAW / "filings" / "sec-submissions-CIK0001670592.json")
    mapping: dict[str, str] = {}
    for idx, accession in enumerate(submissions["filings"]["recent"]["accessionNumber"]):
        form = submissions["filings"]["recent"]["form"][idx]
        filing_date = submissions["filings"]["recent"]["filingDate"][idx]
        primary_doc = submissions["filings"]["recent"]["primaryDocument"][idx]
        slug = primary_doc.lower().replace("/", "-")
        local = f"raw/filings/yeti-{filing_date}-{form.lower().replace('/', '')}-{slug}"
        if (ROOT / local).exists():
            mapping[accession] = local
    return mapping


def fact_record(facts: dict, tag: str, unit: str, year: int, instant: bool) -> dict | None:
    item = facts["us-gaap"].get(tag)
    if not item:
        return None
    rows = item.get("units", {}).get(unit, [])
    target_frame = f"CY{year}Q4I" if instant else f"CY{year}"
    candidates = [row for row in rows if row.get("frame") == target_frame and row.get("form") == "10-K"]
    if not candidates:
        candidates = [
            row
            for row in rows
            if row.get("form") == "10-K"
            and row.get("fp") == "FY"
            and row.get("fy") == year
            and (row.get("start") is None if instant else row.get("start") is not None)
        ]
    if not candidates:
        return None
    return sorted(candidates, key=lambda row: row.get("filed", ""), reverse=True)[0]


def extract_annual_financials() -> list[dict]:
    facts = read_json(RAW / "filings" / "sec-companyfacts-CIK0001670592.json")["facts"]
    source_by_accn = accession_source_map()
    rows: list[dict] = []
    for year in FISCAL_YEARS:
        for metric, (tag, unit) in ANNUAL_TAGS.items():
            record = fact_record(facts, tag, unit, year, instant=False)
            if not record:
                continue
            rows.append(
                {
                    "period": f"FY{year}",
                    "year": year,
                    "statement": "income/cash flow",
                    "metric": metric,
                    "value": record["val"],
                    "unit": unit,
                    "source_file": source_by_accn.get(record["accn"], "raw/filings/sec-companyfacts-CIK0001670592.json"),
                    "source_dataset": "SEC companyfacts",
                    "raw_tag": f"us-gaap:{tag}",
                    "accession": record["accn"],
                    "frame": record.get("frame") or "",
                    "filed": record.get("filed") or "",
                    "start": record.get("start") or "",
                    "end": record.get("end") or "",
                    "notes": "Annual 10-K fact selected by SEC frame/fiscal year.",
                }
            )
        for metric, (tag, unit) in INSTANT_TAGS.items():
            record = fact_record(facts, tag, unit, year, instant=True)
            if not record:
                continue
            rows.append(
                {
                    "period": f"FY{year}",
                    "year": year,
                    "statement": "balance sheet",
                    "metric": metric,
                    "value": record["val"],
                    "unit": unit,
                    "source_file": source_by_accn.get(record["accn"], "raw/filings/sec-companyfacts-CIK0001670592.json"),
                    "source_dataset": "SEC companyfacts",
                    "raw_tag": f"us-gaap:{tag}",
                    "accession": record["accn"],
                    "frame": record.get("frame") or "",
                    "filed": record.get("filed") or "",
                    "start": record.get("start") or "",
                    "end": record.get("end") or "",
                    "notes": "Fiscal year-end balance sheet fact selected by SEC instant frame.",
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def extract_sales_breakdown() -> list[dict]:
    source_file = "raw/filings/yeti-2026-02-27-10-k-yeti-20260103.htm"
    soup = BeautifulSoup((ROOT / source_file).read_text(encoding="utf-8"), "lxml")
    table = None
    for candidate in soup.find_all("table"):
        text = candidate.get_text("|", strip=True)
        if "Net Sales by Channel" in text and "Net Sales by Category" in text:
            table = candidate
            break
    if table is None:
        raise RuntimeError("Could not find YETI net sales breakdown table")

    tokens = [cell.get_text(" ", strip=True) for cell in table.find_all(["td", "th"])]
    years: list[int] = []
    for token in tokens:
        year_match = re.search(r"\b(20\d{2})\b", token)
        if year_match and int(year_match.group(1)) not in years:
            years.append(int(year_match.group(1)))
        if len(years) == 3:
            break

    def values_after(label: str) -> list[float]:
        idx = tokens.index(label)
        vals: list[float] = []
        for token in tokens[idx + 1 :]:
            if re.fullmatch(r"20\d{2}", token) or token.startswith("Net Sales by") or token == ":":
                if vals:
                    break
                continue
            if re.fullmatch(r"\(?\d+\)?", token) or token == "$":
                continue
            if re.fullmatch(r"\d[\d,]*", token):
                vals.append(clean_number(token) * 1000)
                if len(vals) == len(years):
                    break
        if len(vals) != len(years):
            raise RuntimeError(f"Could not parse {len(years)} values after {label!r}: {vals}")
        return vals

    mappings = [
        ("channel", "Wholesale", "Wholesale"),
        ("channel", "Direct-to-consumer", "Direct-to-consumer"),
        ("category", "Coolers & Equipment", "Coolers & Equipment"),
        ("category", "Drinkware", "Drinkware"),
        ("category", "Other", "Other"),
        ("geography", "United States", "United States"),
        ("geography", "International", "International"),
    ]
    rows: list[dict] = []
    table_text_path = OUT / "filings" / "yeti-2025-10k-sales-breakdown-table.txt"
    table_text_path.parent.mkdir(parents=True, exist_ok=True)
    table_text_path.write_text("\n".join(tokens) + "\n", encoding="utf-8")
    for breakdown_type, label, category in mappings:
        values = values_after(label)
        for year, value in zip(years, values, strict=True):
            rows.append(
                {
                    "year": year,
                    "period": f"FY{year}",
                    "breakdown_type": breakdown_type,
                    "category": category,
                    "value": value,
                    "unit": "USD",
                    "source_file": source_file,
                    "extracted_text_file": str(table_text_path.relative_to(ROOT)).replace("\\", "/"),
                    "source_table": "2025 Form 10-K Note 3, net sales by channel/category/geography",
                    "notes": "Values in 10-K table are in thousands; script scales to dollars.",
                }
            )
    return rows


def regex_value(pattern: str, text: str, default: str | None = None) -> str | None:
    match = re.search(pattern, text, flags=re.S)
    if match:
        return match.group(1)
    return default


def metric_from_stockanalysis(html: str, metric_id: str) -> tuple[str | None, str | None]:
    pattern = r'\{id:"' + re.escape(metric_id) + r'".*?value:"([^"]*)".*?hover:(?:"([^"]*)"|([^,}]*))'
    match = re.search(pattern, html, flags=re.S)
    if not match:
        return None, None
    return match.group(1), match.group(2) if match.group(2) is not None else match.group(3)


def extract_market_data() -> list[dict]:
    rows: list[dict] = []
    market_html = (RAW / "other" / "stockanalysis-yeti-market-cap.html").read_text(encoding="utf-8")
    stats_html = (RAW / "other" / "stockanalysis-yeti-statistics.html").read_text(encoding="utf-8")
    forecast_html = (RAW / "other" / "stockanalysis-yeti-forecast.html").read_text(encoding="utf-8")

    quote_date = regex_value(r"quote:\{.*?u:\"([^\"]+)\"", market_html, "")
    for metric_id, label in [
        ("marketcap", "market_cap"),
        ("enterpriseValue", "enterprise_value"),
        ("sharesout", "shares_outstanding"),
        ("peForward", "forward_pe"),
        ("pfcf", "price_to_fcf"),
        ("evEbitda", "ev_ebitda"),
        ("beta", "beta_5y"),
        ("debt", "total_debt_stockanalysis"),
        ("fcf", "free_cash_flow_ltm_stockanalysis"),
    ]:
        value, hover = metric_from_stockanalysis(stats_html, metric_id)
        if value is None:
            continue
        numeric = None
        try:
            numeric = parse_money_string(hover)
        except Exception:
            try:
                numeric = float(value.replace("%", ""))
            except Exception:
                numeric = None
        rows.append(
            {
                "metric": label,
                "value": numeric if numeric is not None else value,
                "display_value": value,
                "as_of": quote_date,
                "source_file": "raw/other/stockanalysis-yeti-statistics.html",
                "source_id": "STOCKANALYSIS-YETI-STATISTICS",
                "notes": f"Extracted StockAnalysis metric id {metric_id}.",
            }
        )

    quote_price = regex_value(r'quote:\{.*?p:([0-9.]+)', market_html)
    if quote_price:
        rows.append(
            {
                "metric": "share_price",
                "value": float(quote_price),
                "display_value": quote_price,
                "as_of": quote_date,
                "source_file": "raw/other/stockanalysis-yeti-market-cap.html",
                "source_id": "STOCKANALYSIS-YETI-MARKET-CAP",
                "notes": "Intraday quote captured in StockAnalysis market-cap page.",
            }
        )

    target = re.search(
        r"targets:\{low:([0-9.]+),high:([0-9.]+),count:([0-9]+),median:([0-9.]+),average:([0-9.]+),updated:\"([^\"]+)\"",
        forecast_html,
    )
    if target:
        for name, value in [
            ("consensus_target_low", target.group(1)),
            ("consensus_target_high", target.group(2)),
            ("consensus_target_count", target.group(3)),
            ("consensus_target_median", target.group(4)),
            ("consensus_target_average", target.group(5)),
        ]:
            rows.append(
                {
                    "metric": name,
                    "value": float(value),
                    "display_value": value,
                    "as_of": target.group(6),
                    "source_file": "raw/other/stockanalysis-yeti-forecast.html",
                    "source_id": "STOCKANALYSIS-YETI-FORECAST",
                    "notes": "Consensus price target field embedded in StockAnalysis forecast page.",
                }
            )

    for metric, pattern in [
        ("consensus_2026_revenue", r"revenueThis:\{last:[0-9.]+,this:([0-9.]+),growth:([0-9.\-]+)"),
        ("consensus_2026_eps", r"epsThis:\{last:[0-9.]+,this:([0-9.]+),growth:([0-9.\-]+)"),
    ]:
        match = re.search(pattern, forecast_html)
        if match:
            rows.append(
                {
                    "metric": metric,
                    "value": float(match.group(1)),
                    "display_value": match.group(1),
                    "as_of": quote_date,
                    "source_file": "raw/other/stockanalysis-yeti-forecast.html",
                    "source_id": "STOCKANALYSIS-YETI-FORECAST",
                    "notes": f"Consensus growth {match.group(2)}%.",
                }
            )

    rows.extend(extract_treasury_and_erp())
    return rows


def extract_treasury_and_erp() -> list[dict]:
    rows: list[dict] = []
    treasury_file = "raw/other/us-treasury-daily-yield-curve-2026.html"
    soup = BeautifulSoup((ROOT / treasury_file).read_text(encoding="utf-8"), "lxml")
    table_rows = []
    for tr in soup.find_all("tr"):
        cells = [cell.get_text(" ", strip=True) for cell in tr.find_all(["th", "td"])]
        if cells:
            table_rows.append(cells)
    headers = table_rows[0]
    ten_year_idx = headers.index("10 Yr")
    data_rows = [row for row in table_rows[1:] if len(row) > ten_year_idx and re.match(r"\d{2}/\d{2}/2026", row[0])]
    latest = sorted(data_rows, key=lambda row: datetime.strptime(row[0], "%m/%d/%Y"))[-1]
    rows.append(
        {
            "metric": "risk_free_rate_10y_treasury",
            "value": float(latest[ten_year_idx]) / 100,
            "display_value": latest[ten_year_idx] + "%",
            "as_of": latest[0],
            "source_file": treasury_file,
            "source_id": "US-TREASURY-DAILY-RATES",
            "notes": "Latest 2026 daily Treasury par yield curve 10-year rate in fetched table.",
        }
    )

    kroll_file = "raw/other/kroll-us-equity-risk-premium.html"
    kroll_html = (ROOT / kroll_file).read_text(encoding="utf-8")
    erp_match = re.search(r"recommended U\.S\. Equity Risk Premium to ([0-9.]+)%", kroll_html, flags=re.I)
    erp = erp_match.group(1) if erp_match else None
    if erp:
        rows.append(
            {
                "metric": "equity_risk_premium_kroll",
                "value": float(erp) / 100,
                "display_value": erp + "%",
                "as_of": regex_value(r'<meta name="PublishedDate" content="([^"]+)"', kroll_html, ""),
                "source_file": kroll_file,
                "source_id": "KROLL-ERP-2026",
                "notes": "Kroll recommended U.S. equity risk premium reference.",
            }
        )
    return rows


def extract_peer_valuation() -> list[dict]:
    peers = {
        "YETI": "stockanalysis-yeti-statistics.html",
        "GOLF": "stockanalysis-golf-statistics.html",
        "MAT": "stockanalysis-mat-statistics.html",
        "NWL": "stockanalysis-nwl-statistics.html",
        "DTC": "stockanalysis-dtc-statistics.html",
    }
    metric_ids = {
        "market_cap": "marketcap",
        "enterprise_value": "enterpriseValue",
        "ev_ebitda": "evEbitda",
        "forward_pe": "peForward",
        "price_to_fcf": "pfcf",
        "gross_margin": "grossMargin",
        "operating_margin": "operatingMargin",
        "fcf_margin": "fcfMargin",
    }
    rows: list[dict] = []
    for ticker, filename in peers.items():
        html = (RAW / "other" / filename).read_text(encoding="utf-8")
        quote_date = regex_value(r"quote:\{.*?u:\"([^\"]+)\"", html, "")
        for metric, metric_id in metric_ids.items():
            value, hover = metric_from_stockanalysis(html, metric_id)
            if value is None:
                continue
            if value.lower() == "n/a" or (hover and hover.lower() == "n/a"):
                continue
            try:
                numeric = parse_money_string(hover)
            except Exception:
                numeric = float(value.replace("%", ""))
            rows.append(
                {
                    "ticker": ticker,
                    "metric": metric,
                    "value": numeric,
                    "display_value": value,
                    "as_of": quote_date,
                    "source_file": f"raw/other/{filename}",
                    "notes": f"Extracted StockAnalysis metric id {metric_id}.",
                }
            )
    return rows


def extract_guidance() -> list[dict]:
    source_file = "raw/other/yeti-q4-fy2025-results-pr.html"
    text = BeautifulSoup((ROOT / source_file).read_text(encoding="utf-8"), "lxml").get_text("\n", strip=True)
    start = text.index("For Fiscal 2026 compared to Fiscal 2025, YETI expects:")
    block = text[start : start + 1800]
    guidance = [
        ("adjusted_sales_growth_low", r"Adjusted sales\s+to increase between ([0-9.]+)%", "percent"),
        ("adjusted_sales_growth_high", r"Adjusted sales\s+to increase between [0-9.]+% to ([0-9.]+)%", "percent"),
        ("adjusted_operating_margin", r"Adjusted operating income as a percentage of adjusted sales\s+of approximately ([0-9.]+)%", "percent"),
        ("effective_tax_rate", r"An effective tax rate\s+of approximately ([0-9.]+)%", "percent"),
        ("adjusted_eps_low", r"Adjusted net income per diluted share\s+between \$([0-9.]+)", "USD/share"),
        ("adjusted_eps_high", r"Adjusted net income per diluted share\s+between \$[0-9.]+ and \$([0-9.]+)", "USD/share"),
        ("diluted_shares", r"Diluted weighted average shares outstanding\s+of approximately ([0-9.]+) million", "shares"),
        ("expected_share_repurchases", r"\$([0-9.]+)\s*million in expected share repurchases", "USD"),
        ("capex_low", r"Capital expenditures\s+between \$([0-9.]+) million", "USD"),
        ("capex_high", r"Capital expenditures\s+between \$[0-9.]+ million and \$([0-9.]+) million", "USD"),
        ("free_cash_flow_low", r"Free cash flow\s+between \$([0-9.]+) million", "USD"),
        ("free_cash_flow_high", r"Free cash flow\s+between \$[0-9.]+ million and \$([0-9.]+) million", "USD"),
    ]
    rows: list[dict] = []
    for metric, pattern, unit in guidance:
        match = re.search(pattern, block, flags=re.S)
        if not match:
            continue
        value = float(match.group(1))
        if unit == "percent":
            stored_value = value / 100
        elif unit in {"USD", "shares"}:
            stored_value = value * 1_000_000
        else:
            stored_value = value
        rows.append(
            {
                "metric": metric,
                "value": stored_value,
                "display_value": match.group(1),
                "unit": unit,
                "source_file": source_file,
                "source_id": "YETI-IR-Q4-2025-PR",
                "notes": "Parsed from Fiscal 2026 outlook block in Q4/FY2025 results release.",
            }
        )
    (OUT / "guidance_2026_context.txt").write_text(block + "\n", encoding="utf-8")
    return rows


def build_wide_financials(rows: list[dict]) -> list[dict]:
    metrics = sorted({row["metric"] for row in rows})
    wide: list[dict] = []
    for year in FISCAL_YEARS:
        row = {"year": year, "period": f"FY{year}"}
        for metric in metrics:
            match = next((item for item in rows if item["year"] == year and item["metric"] == metric), None)
            row[metric] = match["value"] if match else ""
        row["free_cash_flow"] = (
            float(row.get("operating_cash_flow") or 0) - float(row.get("capex") or 0)
            if row.get("operating_cash_flow") != "" and row.get("capex") != ""
            else ""
        )
        row["funded_debt"] = (
            float(row.get("current_debt") or 0) + float(row.get("long_term_debt") or 0)
            if row.get("current_debt") != "" and row.get("long_term_debt") != ""
            else ""
        )
        wide.append(row)
    return wide


def main() -> int:
    annual = extract_annual_financials()
    write_csv(
        OUT / "yeti_financials_annual.csv",
        annual,
        [
            "period",
            "year",
            "statement",
            "metric",
            "value",
            "unit",
            "source_file",
            "source_dataset",
            "raw_tag",
            "accession",
            "frame",
            "filed",
            "start",
            "end",
            "notes",
        ],
    )
    write_csv(OUT / "yeti_financials_wide.csv", build_wide_financials(annual))
    write_csv(OUT / "yeti_sales_breakdown.csv", extract_sales_breakdown())
    write_csv(OUT / "yeti_market_data.csv", extract_market_data())
    write_csv(OUT / "peer_valuation.csv", extract_peer_valuation())
    write_csv(OUT / "yeti_2026_guidance.csv", extract_guidance())
    manifest = {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "outputs": [
            "extracted/yeti_financials_annual.csv",
            "extracted/yeti_financials_wide.csv",
            "extracted/yeti_sales_breakdown.csv",
            "extracted/yeti_market_data.csv",
            "extracted/peer_valuation.csv",
            "extracted/yeti_2026_guidance.csv",
            "extracted/guidance_2026_context.txt",
            "extracted/filings/yeti-2025-10k-sales-breakdown-table.txt",
        ],
    }
    (OUT / "extraction_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
