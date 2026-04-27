"""Walk every Q4/FY press release table_05 and table_06 and assemble a single
long-form CSV: extracted/segment_history.csv

Why: we need a multi-year series of revenue and gross margin by
(segment, brand) to drive the model and to test the variant view that
freight-tailwind GM is partly cyclical.
"""
from __future__ import annotations

import csv
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parent.parent
TABLES = REPO / "extracted" / "press_tables"
OUT = REPO / "extracted" / "segment_history.csv"


def _to_int(x: str) -> int | None:
    s = x.replace(",", "").replace("$", "").replace("(", "-").replace(")", "").strip()
    if not s or s in ("-", "—", "%"):
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


def _to_float_pct(x: str) -> float | None:
    s = x.replace(",", "").replace("(", "-").replace(")", "").strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def parse_table_5(rows: list[list[str]]) -> dict:
    """NET SALES table. Columns: Q (current), Q (prior), YTD (current), YTD (prior).
    Note: layout is column-padded. We'll extract the four numeric fields per row.
    """
    out = {"net_sales": {}}
    segment = None
    for row in rows:
        first = row[0].strip() if row else ""
        if not first:
            continue
        if first.endswith("segment"):
            segment = first.replace(" segment", "").strip()
            continue
        if first in ("Vita Coco Coconut Water", "Private Label", "Other"):
            # numeric cells - filter to non-empty non-$ non-, cells
            nums = [c for c in row[1:] if c.strip() not in ("", "$", ",")]
            ints = [n for n in (_to_int(c) for c in nums) if n is not None]
            if len(ints) >= 4:
                out["net_sales"][(segment, first)] = ints[:4]  # q_curr, q_prior, ytd_curr, ytd_prior
    return out


def parse_table_6(rows: list[list[str]]) -> dict:
    out = {"cogs": {}, "gross_profit": {}, "gross_margin": {}}
    section = None
    for row in rows:
        first = row[0].strip() if row else ""
        if first == "Cost of goods sold":
            section = "cogs"; continue
        if first == "Gross profit":
            section = "gross_profit"; continue
        if first == "Gross margin":
            section = "gross_margin"; continue
        if not first or not section:
            continue
        if first in ("Total cost of goods sold", "Total gross profit", "Consolidated"):
            key = "Consolidated"
        elif first.endswith("segment"):
            key = first.replace(" segment", "").strip()
        else:
            continue
        nums = [c for c in row[1:] if c.strip() not in ("", "$", ",", "%")]
        if section == "gross_margin":
            vals = [v for v in (_to_float_pct(c) for c in nums) if v is not None]
        else:
            vals = [v for v in (_to_int(c) for c in nums) if v is not None]
        if len(vals) >= 4:
            out[section][key] = vals[:4]
    return out


def main() -> None:
    # Press release file -> (period_label, period_end_curr, period_end_prior)
    pr_files = sorted(TABLES.glob("PR_*__table_05.csv"))
    long_rows: list[dict] = []

    for f5 in pr_files:
        f6 = pathlib.Path(str(f5).replace("__table_05.csv", "__table_06.csv"))
        # Filename like PR_Q4-FY2025_26-000019__table_05.csv
        stem = f5.stem
        m = re.match(r"PR_(Q[1-4](?:-FY\d{4})?)-?(\d{4})?_(\d+-\d+)__table_05", stem.replace("__table_05.csv", "__table_05"))
        if not m:
            # Match more loosely
            m = re.match(r"PR_(Q[1-4]-FY\d{4}|Q[1-4]-\d{4})_", stem)
        period = stem.split("_")[1]  # like 'Q4-FY2025'
        accn = stem.split("_")[2].split("__")[0]
        # period_end inferred from label
        label_to_end = {
            "Q1-2024": ("2024-03-31", "2023-03-31", "Q1"),
            "Q2-2024": ("2024-06-30", "2023-06-30", "Q2"),
            "Q3-2024": ("2024-09-30", "2023-09-30", "Q3"),
            "Q4-FY2023": ("2023-12-31", "2022-12-31", "Q4"),
            "Q4-FY2024": ("2024-12-31", "2023-12-31", "Q4"),
            "Q4-FY2025": ("2025-12-31", "2024-12-31", "Q4"),
            "Q1-2025":  ("2025-03-31", "2024-03-31", "Q1"),
            "Q2-2025":  ("2025-06-30", "2024-06-30", "Q2"),
            "Q3-2025":  ("2025-09-30", "2024-09-30", "Q3"),
        }
        if period not in label_to_end:
            print(f"skip {period} (no period mapping)")
            continue
        end_curr, end_prior, qlabel = label_to_end[period]

        with f5.open(encoding="utf-8", newline="") as f:
            t5 = list(csv.reader(f))
        ns = parse_table_5(t5)["net_sales"]
        with f6.open(encoding="utf-8", newline="") as f:
            t6 = list(csv.reader(f))
        ts6 = parse_table_6(t6)

        # Quarterly slice for sales by segment+brand
        for (seg, brand), (q_curr, q_prior, ytd_curr, ytd_prior) in ns.items():
            long_rows.append({
                "label": period,
                "segment": seg,
                "brand": brand,
                "metric": "net_sales_q",
                "period_end": end_curr,
                "fp": qlabel,
                "value": q_curr,
                "source_accn": accn,
            })
            long_rows.append({
                "label": period + " (yr ago)",
                "segment": seg,
                "brand": brand,
                "metric": "net_sales_q",
                "period_end": end_prior,
                "fp": qlabel,
                "value": q_prior,
                "source_accn": accn,
            })
            long_rows.append({
                "label": period,
                "segment": seg,
                "brand": brand,
                "metric": "net_sales_ytd",
                "period_end": end_curr,
                "fp": qlabel + "-YTD",
                "value": ytd_curr,
                "source_accn": accn,
            })
            long_rows.append({
                "label": period + " (yr ago)",
                "segment": seg,
                "brand": brand,
                "metric": "net_sales_ytd",
                "period_end": end_prior,
                "fp": qlabel + "-YTD",
                "value": ytd_prior,
                "source_accn": accn,
            })
        # COGS / GP / GM by segment
        for metric, m in [("cogs", ts6["cogs"]), ("gross_profit", ts6["gross_profit"])]:
            for seg, vals in m.items():
                q_curr, q_prior, ytd_curr, ytd_prior = vals
                long_rows.append({"label": period, "segment": seg, "brand": "", "metric": f"{metric}_q",   "period_end": end_curr,  "fp": qlabel,           "value": q_curr,   "source_accn": accn})
                long_rows.append({"label": period, "segment": seg, "brand": "", "metric": f"{metric}_ytd", "period_end": end_curr,  "fp": qlabel+"-YTD",    "value": ytd_curr, "source_accn": accn})
                long_rows.append({"label": period+" (yr ago)", "segment": seg, "brand": "", "metric": f"{metric}_q",   "period_end": end_prior, "fp": qlabel,           "value": q_prior,  "source_accn": accn})
                long_rows.append({"label": period+" (yr ago)", "segment": seg, "brand": "", "metric": f"{metric}_ytd", "period_end": end_prior, "fp": qlabel+"-YTD",    "value": ytd_prior,"source_accn": accn})
        for seg, vals in ts6["gross_margin"].items():
            q_curr, q_prior, ytd_curr, ytd_prior = vals
            long_rows.append({"label": period, "segment": seg, "brand": "", "metric": "gross_margin_pct_q",   "period_end": end_curr,  "fp": qlabel,           "value": q_curr,   "source_accn": accn})
            long_rows.append({"label": period, "segment": seg, "brand": "", "metric": "gross_margin_pct_ytd", "period_end": end_curr,  "fp": qlabel+"-YTD",    "value": ytd_curr, "source_accn": accn})
            long_rows.append({"label": period+" (yr ago)", "segment": seg, "brand": "", "metric": "gross_margin_pct_q",   "period_end": end_prior, "fp": qlabel,           "value": q_prior,  "source_accn": accn})
            long_rows.append({"label": period+" (yr ago)", "segment": seg, "brand": "", "metric": "gross_margin_pct_ytd", "period_end": end_prior, "fp": qlabel+"-YTD",    "value": ytd_prior,"source_accn": accn})

    with OUT.open("w", encoding="utf-8", newline="") as f:
        if long_rows:
            w = csv.DictWriter(f, fieldnames=list(long_rows[0].keys()))
            w.writeheader()
            for r in long_rows:
                w.writerow(r)
    print(f"OK {OUT.relative_to(REPO).as_posix()} ({len(long_rows)} rows)")


if __name__ == "__main__":
    main()
