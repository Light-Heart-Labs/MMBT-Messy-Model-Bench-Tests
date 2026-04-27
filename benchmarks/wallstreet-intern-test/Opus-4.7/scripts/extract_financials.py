"""Pull a curated set of XBRL facts from raw/other/edgar_companyfacts_*.json
into clean CSVs in extracted/.

Two outputs:
  extracted/annual.csv    - one row per fiscal year, FY-tagged 10-K data
  extracted/quarterly.csv - one row per quarter, Q-tagged 10-Q + Q4 derived

Each row carries the source accession so any cell can be traced back to a
single 10-K or 10-Q in raw/filings/.
"""
from __future__ import annotations

import csv
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
COMPANYFACTS = REPO / "raw" / "other" / "edgar_companyfacts_0001482981.json"
OUT_DIR = REPO / "extracted"

# canonical name -> list of XBRL tags to try (first hit wins)
TAGS = {
    "revenue":          ["RevenueFromContractWithCustomerIncludingAssessedTax", "Revenues"],
    "cogs":             ["CostOfGoodsAndServicesSold", "CostOfRevenue"],
    "gross_profit":     ["GrossProfit"],
    "sga":              ["SellingGeneralAndAdministrativeExpense"],
    "operating_income": ["OperatingIncomeLoss"],
    "non_operating":    ["NonoperatingIncomeExpense"],
    "interest_expense": ["InterestExpense"],
    "pretax_income":    ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest", "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"],
    "income_tax":       ["IncomeTaxExpenseBenefit"],
    "net_income":       ["NetIncomeLoss"],
    "eps_basic":        ["EarningsPerShareBasic"],
    "eps_diluted":      ["EarningsPerShareDiluted"],
    "shares_basic":     ["WeightedAverageNumberOfSharesOutstandingBasic"],
    "shares_diluted":   ["WeightedAverageNumberOfDilutedSharesOutstanding"],
    # balance sheet
    "cash":             ["CashAndCashEquivalentsAtCarryingValue"],
    "receivables":      ["AccountsReceivableNetCurrent", "ReceivablesNetCurrent"],
    "inventory":        ["InventoryNet"],
    "total_current_assets": ["AssetsCurrent"],
    "total_assets":     ["Assets"],
    "accounts_payable": ["AccountsPayableCurrent"],
    "total_current_liabilities": ["LiabilitiesCurrent"],
    "total_liabilities": ["Liabilities"],
    "stockholders_equity": ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
    # cash flow
    "cfo":              ["NetCashProvidedByUsedInOperatingActivities"],
    "cfi":              ["NetCashProvidedByUsedInInvestingActivities"],
    "cff":              ["NetCashProvidedByUsedInFinancingActivities"],
    "capex":            ["PaymentsToAcquirePropertyPlantAndEquipment"],
    "depreciation_amort": ["DepreciationDepletionAndAmortization", "DepreciationAndAmortization"],
    "stock_based_comp": ["ShareBasedCompensation"],
}


def get_facts(facts: dict, tags: list[str]) -> list[dict]:
    for tag in tags:
        if tag in facts.get("us-gaap", {}):
            units = facts["us-gaap"][tag]["units"]
            # take USD if present, else first unit (handles per-share, shares-outstanding)
            if "USD" in units:
                return units["USD"]
            return next(iter(units.values()))
    return []


def latest_per_period(rows: list[dict], fp_filter: str | None = None) -> dict[str, dict]:
    """Group by 'end' date keeping the most recently filed value (handles restatements).
    fp_filter: 'FY' to keep only annual rows, 'Q1'/'Q2'/'Q3' for quarterly, None for any.
    """
    by_end: dict[str, dict] = {}
    for r in rows:
        if fp_filter and r.get("fp") != fp_filter:
            continue
        if fp_filter == "FY" and r.get("form") != "10-K":
            continue
        end = r["end"]
        if end not in by_end or r["filed"] > by_end[end]["filed"]:
            by_end[end] = r
    return by_end


def extract_annual(data: dict) -> list[dict]:
    """One row per fiscal year. Year is derived from the 'end' date."""
    facts = data["facts"]
    # Build a master set of years from revenue
    rev_rows = get_facts(facts, TAGS["revenue"])
    annual_rev = latest_per_period(rev_rows, fp_filter="FY")
    years = sorted(annual_rev.keys())
    out = []
    for end in years:
        year = end[:4]
        row: dict = {"period_end": end, "fy": year}
        # revenue's accession seeds the row
        row["source_accn"] = annual_rev[end]["accn"]
        row["source_filed"] = annual_rev[end]["filed"]
        for name, tag_list in TAGS.items():
            rows = get_facts(facts, tag_list)
            byp = latest_per_period(rows, fp_filter="FY")
            v = byp.get(end, {}).get("val")
            row[name] = v
        out.append(row)
    return out


def extract_quarterly(data: dict) -> list[dict]:
    """One row per fiscal quarter (Q1/Q2/Q3 from 10-Q; Q4 derived from FY - Q1Q2Q3 of prior 10-Q facts)."""
    facts = data["facts"]
    # Use revenue rows tagged Q1/Q2/Q3 from 10-Q
    rev_rows = get_facts(facts, TAGS["revenue"])
    out_rows: list[dict] = []
    # collect Q1/Q2/Q3 entries
    by_quarter_end: dict[str, dict] = {}
    for r in rev_rows:
        if r.get("form") != "10-Q":
            continue
        if r.get("fp") not in ("Q1", "Q2", "Q3"):
            continue
        end = r["end"]
        if end not in by_quarter_end or r["filed"] > by_quarter_end[end]["filed"]:
            by_quarter_end[end] = r
    for end in sorted(by_quarter_end.keys()):
        rec = by_quarter_end[end]
        row = {
            "period_end": end,
            "fy": end[:4],
            "fp": rec["fp"],
            "source_accn": rec["accn"],
            "source_filed": rec["filed"],
        }
        # for each tag, find the value at this end with the same fp
        for name, tag_list in TAGS.items():
            rows = get_facts(facts, tag_list)
            cand = [r for r in rows if r.get("end") == end and r.get("fp") == rec["fp"] and r.get("form") in ("10-Q", "10-K")]
            cand.sort(key=lambda r: r["filed"], reverse=True)
            row[name] = cand[0]["val"] if cand else None
        out_rows.append(row)
    return out_rows


def write_csv(rows: list[dict], path: pathlib.Path) -> None:
    if not rows:
        print(f"(no rows for {path.name})")
        return
    fieldnames = list(rows[0].keys())
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"OK {path.relative_to(REPO).as_posix()} ({len(rows)} rows, {len(fieldnames)} cols)")


def main() -> None:
    if not COMPANYFACTS.exists():
        print(f"missing {COMPANYFACTS}")
        sys.exit(1)
    data = json.loads(COMPANYFACTS.read_text(encoding="utf-8"))
    annual = extract_annual(data)
    quarterly = extract_quarterly(data)
    write_csv(annual, OUT_DIR / "annual.csv")
    write_csv(quarterly, OUT_DIR / "quarterly.csv")


if __name__ == "__main__":
    main()
