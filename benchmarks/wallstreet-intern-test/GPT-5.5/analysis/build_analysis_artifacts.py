import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path):
    with (ROOT / path).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(value):
    if value in (None, ""):
        return None
    return float(str(value).replace(",", ""))


def model_blocks():
    blocks = {}
    for line in (ROOT / "model/key-outputs.ndjson").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        outer = json.loads(line)
        inner = json.loads(outer["ndjson"])
        blocks[outer["name"]] = inner["values"]
    return blocks


def row_by_label(table, label):
    for row in table:
        if row and row[0] == label:
            return row
    raise KeyError(label)


def metric_row(rows, metric):
    for row in rows:
        if row["metric"] == metric:
            return row
    raise KeyError(metric)


def sales_row(rows, segment_type, segment, year="2025"):
    for row in rows:
        if row["breakdown_type"] == segment_type and row["category"] == segment and row["year"] == year:
            return row
    raise KeyError((segment_type, segment, year))


def peer_metric(rows, ticker, metric):
    for row in rows:
        if row["ticker"] == ticker and row["metric"] == metric:
            return row
    raise KeyError((ticker, metric))


def add(rows, trace_id, metric, value, source_chain, model_ref="", notes=""):
    rows.append(
        {
            "trace_id": trace_id,
            "metric": metric,
            "value": value,
            "source_chain": source_chain,
            "model_ref": model_ref,
            "notes": notes,
        }
    )


def main():
    blocks = model_blocks()
    cover = blocks["cover"]
    assumptions = blocks["assumptions"]
    model = blocks["base_model"]
    valuation = blocks["valuation"]
    scenarios = blocks["scenarios"]

    financials = read_csv("extracted/yeti_financials_wide.csv")
    sales = read_csv("extracted/yeti_sales_breakdown.csv")
    market = read_csv("extracted/yeti_market_data.csv")
    peers = read_csv("extracted/peer_valuation.csv")
    guidance = read_csv("extracted/yeti_2026_guidance.csv")

    fy2025 = next(row for row in financials if row["year"] == "2025")
    fy2024 = next(row for row in financials if row["year"] == "2024")
    source_10k_chain = "raw/filings/yeti-2026-02-27-10-k-yeti-20260103.htm -> extracted/yeti_financials_annual.csv -> extracted/yeti_financials_wide.csv"
    sales_chain = "raw/filings/yeti-2026-02-27-10-k-yeti-20260103.htm -> extracted/filings/yeti-2025-10k-sales-breakdown-table.txt -> extracted/yeti_sales_breakdown.csv"
    market_chain = "raw/other/stockanalysis-yeti-market-cap.html and raw/other/stockanalysis-yeti-statistics.html -> extracted/yeti_market_data.csv"
    forecast_chain = "model/yeti_investment_model.xlsx -> model/key-outputs.ndjson"
    guidance_chain = "raw/other/yeti-q4-fy2025-results-pr.html -> extracted/yeti_2026_guidance.csv"
    peer_chain = "raw/other/stockanalysis-*-statistics.html -> extracted/peer_valuation.csv"
    transcript_chain = "raw/transcripts/yeti-q4-2025-earnings-call-transcript.pdf -> extracted/transcripts/yeti-q4-2025-earnings-call-transcript.txt"

    rows = []
    add(rows, "T000", "source pull and memo date", "2026-04-27", "sources.md and tool-log.md", "", "The repo was built from sources fetched and logged on this date.")
    add(rows, "T001", "current share price", row_by_label(cover, "Current price")[1], market_chain, "Cover!B7")
    add(rows, "T002", "market capitalization", row_by_label(cover, "Market cap")[1], market_chain, "Cover!B9")
    add(rows, "T003", "12-month price target", row_by_label(cover, "12-month price target")[1], forecast_chain, "Cover!B6 / Valuation!B19")
    add(rows, "T004", "upside to target", row_by_label(cover, "Implied upside")[1], forecast_chain, "Cover!B8 / Valuation!B20")
    add(rows, "T005", "FY2025 revenue", num(fy2025["revenue"]) / 1_000_000, source_10k_chain, "Model!D5")
    add(rows, "T006", "FY2025 revenue growth", num(fy2025["revenue"]) / num(fy2024["revenue"]) - 1, source_10k_chain, "Model!D6")
    add(rows, "T007", "FY2025 free cash flow", num(fy2025["free_cash_flow"]) / 1_000_000, source_10k_chain, "Model!D46")
    add(rows, "T008", "FY2025 FCF margin", num(fy2025["free_cash_flow"]) / num(fy2025["revenue"]), source_10k_chain, "Model!D46 / Model!D5")
    add(rows, "T009", "FY2025 operating margin", row_by_label(model, "Operating margin")[3], source_10k_chain, "Model!D12")
    add(rows, "T010", "FY2025 gross margin", row_by_label(model, "Gross margin")[3], source_10k_chain, "Model!D8")
    add(rows, "T011", "FY2025 DTC sales", num(sales_row(sales, "channel", "Direct-to-consumer")["value"]) / 1_000_000, sales_chain, "Historical sales breakdown")
    add(rows, "T012", "FY2025 wholesale sales", num(sales_row(sales, "channel", "Wholesale")["value"]) / 1_000_000, sales_chain, "Historical sales breakdown")
    add(rows, "T013", "FY2025 international sales", num(sales_row(sales, "geography", "International")["value"]) / 1_000_000, sales_chain, "Historical sales breakdown")
    add(rows, "T014", "FY2025 international share of sales", num(sales_row(sales, "geography", "International")["value"]) / num(fy2025["revenue"]), sales_chain, "Historical sales breakdown / Model!D5")
    add(rows, "T015", "FY2026 revenue growth assumption", row_by_label(model, "Revenue growth")[4], guidance_chain, "Assumptions!B26 / Model!E6")
    add(rows, "T016", "FY2026 revenue forecast", row_by_label(model, "Revenue")[4], forecast_chain, "Model!E5")
    add(rows, "T017", "FY2026 free cash flow forecast", row_by_label(model, "Free cash flow")[4], forecast_chain, "Model!E46")
    add(rows, "T018", "WACC", row_by_label(assumptions, "WACC")[1], market_chain, "Assumptions!B18")
    add(rows, "T019", "terminal growth", row_by_label(assumptions, "Terminal growth - base")[1], forecast_chain, "Assumptions!B19")
    add(rows, "T020", "DCF value per share", row_by_label(valuation, "DCF value / share")[1], forecast_chain, "Valuation!B16")
    add(rows, "T021", "EV/EBITDA value per share", row_by_label(valuation, "EV/EBITDA value / share")[1], forecast_chain, "Valuation!B17")
    add(rows, "T022", "P/E value per share", row_by_label(valuation, "P/E value / share")[1], forecast_chain, "Valuation!B18")
    add(rows, "T023", "bear scenario probability and value", f'{scenarios[1][1]} probability; {scenarios[1][34]} per share', forecast_chain, "Scenarios!B5 and Scenarios!AI5")
    add(rows, "T024", "base scenario probability and value", f'{scenarios[2][1]} probability; {scenarios[2][34]} per share', forecast_chain, "Scenarios!B6 and Scenarios!AI6")
    add(rows, "T025", "bull scenario probability and value", f'{scenarios[3][1]} probability; {scenarios[3][34]} per share', forecast_chain, "Scenarios!B7 and Scenarios!AI7")
    add(rows, "T026", "probability-weighted DCF value", scenarios[6][1], forecast_chain, "Scenarios!B10")
    add(rows, "T027", "consensus target average", row_by_label(valuation, "Consensus target average")[1], market_chain, "Valuation!B24")
    add(rows, "T028", "consensus target median", row_by_label(valuation, "Consensus target median")[1], market_chain, "Valuation!B25")
    add(rows, "T029", "consensus 2026 revenue", row_by_label(valuation, "Consensus 2026 revenue")[1], market_chain, "Valuation!B26")
    add(rows, "T030", "consensus 2026 EPS", row_by_label(valuation, "Consensus 2026 EPS")[1], market_chain, "Valuation!B27")
    add(rows, "T031", "YETI EV/EBITDA", peer_metric(peers, "YETI", "ev_ebitda")["value"], peer_chain, "Peers tab")
    add(rows, "T032", "GOLF EV/EBITDA", peer_metric(peers, "GOLF", "ev_ebitda")["value"], peer_chain, "Peers tab")
    add(rows, "T033", "MAT EV/EBITDA", peer_metric(peers, "MAT", "ev_ebitda")["value"], peer_chain, "Peers tab")
    add(rows, "T034", "NWL EV/EBITDA", peer_metric(peers, "NWL", "ev_ebitda")["value"], peer_chain, "Peers tab")
    for metric in ["adjusted_eps_low", "adjusted_eps_high", "free_cash_flow_low", "free_cash_flow_high", "expected_share_repurchases", "capex_low", "capex_high"]:
        row = metric_row(guidance, metric)
        add(rows, f"T{35 + ['adjusted_eps_low','adjusted_eps_high','free_cash_flow_low','free_cash_flow_high','expected_share_repurchases','capex_low','capex_high'].index(metric):03d}", f"FY2026 guidance {metric}", row["value"], guidance_chain, "Guidance extraction")
    add(rows, "T042", "2026 incremental tariff gross-margin impact", "200 bps", transcript_chain, "Transcript lines 372-374", "Management said 2026 guide embeds about 200 bps incremental impact from higher tariff costs.")
    add(rows, "T043", "2026 tariff cost versus 2024", "$80 million and 430 bps", transcript_chain, "Transcript lines 401-406", "Used as a risk framing item, not a model input.")

    out = ROOT / "analysis/memo_trace_table.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["trace_id", "metric", "value", "source_chain", "model_ref", "notes"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {out.relative_to(ROOT)} with {len(rows)} trace rows")


if __name__ == "__main__":
    main()
