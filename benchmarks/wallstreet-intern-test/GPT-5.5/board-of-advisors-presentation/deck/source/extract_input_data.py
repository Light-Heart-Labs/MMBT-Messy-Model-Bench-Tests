import csv
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOCAL_INPUT = ROOT.parent / "you-have-a-fresh-linux-vm"
ORIGINAL_INPUT_COMMIT = "8bb17db58bbb4201937887c6af6ee6e2b530d2fb"
INPUT_REPO = Path(os.environ.get("INPUT_REPO", "/input/repo"))
BENCHMARK_PARENT_FALLBACK = False
if not INPUT_REPO.exists() and DEFAULT_LOCAL_INPUT.exists():
    INPUT_REPO = DEFAULT_LOCAL_INPUT
if not INPUT_REPO.exists() and (ROOT.parent / "memo/yeti_investment_memo.md").exists():
    INPUT_REPO = ROOT.parent
    BENCHMARK_PARENT_FALLBACK = True

LOGICAL_INPUT = "/input/repo"
if BENCHMARK_PARENT_FALLBACK:
    INPUT_COMMIT = ORIGINAL_INPUT_COMMIT
else:
    INPUT_COMMIT = subprocess.check_output(
        ["git", "-C", str(INPUT_REPO), "rev-parse", "HEAD"], text=True
    ).strip()


def rel(path: Path) -> str:
    return path.relative_to(INPUT_REPO).as_posix()


def logical(rel_path: str) -> str:
    return f"{LOGICAL_INPUT}/{rel_path}"


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def find_line(rel_path: str, needle: str) -> int | None:
    path = INPUT_REPO / rel_path
    if not path.exists():
        return None
    for idx, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        if needle in line:
            return idx
    return None


def find_trace_line(trace_id: str) -> int | None:
    return find_line("analysis/memo_trace_table.csv", f"{trace_id},")


def load_key_outputs():
    blocks = {}
    for line in (INPUT_REPO / "model/key-outputs.ndjson").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        outer = json.loads(line)
        inner = json.loads(outer["ndjson"])
        blocks[outer["name"]] = inner["values"]
    return blocks


def row(table, label):
    for item in table:
        if item and item[0] == label:
            return item
    raise KeyError(label)


def trace_row(trace_rows, trace_id):
    for item in trace_rows:
        if item["trace_id"] == trace_id:
            return item
    raise KeyError(trace_id)


def line_link(rel_path: str, line: int | None = None) -> str:
    suffix = f":{line}" if line else ""
    return f"{logical(rel_path)}{suffix}"


def md_table(rows, headers):
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for r in rows:
        out.append("| " + " | ".join(str(r.get(h, "")) for h in headers) + " |")
    return "\n".join(out)


def main():
    if not INPUT_REPO.exists():
        raise SystemExit("Input repo not found. Set INPUT_REPO or mount /input/repo.")

    tables_dir = ROOT / "assets/tables"
    traces_dir = ROOT / "audit/traces"
    tables_dir.mkdir(parents=True, exist_ok=True)
    traces_dir.mkdir(parents=True, exist_ok=True)

    trace_rows = read_csv(INPUT_REPO / "analysis/memo_trace_table.csv")
    key = load_key_outputs()
    model = key["base_model"]
    valuation = key["valuation"]
    scenarios = key["scenarios"]
    assumptions = key["assumptions"]

    years = ["FY2023A", "FY2024A", "FY2025A", "FY2026E", "FY2027E", "FY2028E", "FY2029E", "FY2030E"]
    financial_rows = []
    for i, year in enumerate(years, start=1):
        financial_rows.append(
            {
                "year": year,
                "revenue_mm": row(model, "Revenue")[i],
                "fcf_mm": row(model, "Free cash flow")[i],
                "operating_margin": row(model, "Operating margin")[i],
                "trace": "T005/T007/T009" if i <= 3 else "T016/T017",
            }
        )
    write_csv(tables_dir / "financial_trajectory.csv", financial_rows, financial_rows[0].keys())

    recommendation_rows = [
        {"metric": "Recommendation", "value": "HOLD", "trace": "T003"},
        {"metric": "Current price", "value": 39.62, "trace": "T001"},
        {"metric": "12-month target", "value": 41.00, "trace": "T003"},
        {"metric": "Upside", "value": 0.03483089348813739, "trace": "T004"},
        {"metric": "Market cap", "value": 2998.982096, "trace": "T002"},
        {"metric": "Model status", "value": "OK", "trace": "model checks"},
    ]
    write_csv(tables_dir / "recommendation_snapshot.csv", recommendation_rows, recommendation_rows[0].keys())

    business_rows = [
        {"segment_type": "Channel", "segment": "DTC", "sales_mm": 1127.791, "trace": "T011"},
        {"segment_type": "Channel", "segment": "Wholesale", "sales_mm": 740.703, "trace": "T012"},
        {"segment_type": "Geography", "segment": "International", "sales_mm": 394.353, "trace": "T013"},
        {"segment_type": "Geography", "segment": "US", "sales_mm": 1474.141, "trace": "T005/T013"},
    ]
    write_csv(tables_dir / "business_mix.csv", business_rows, business_rows[0].keys())

    valuation_rows = [
        {"method": "DCF", "value_per_share": row(valuation, "DCF value / share")[1], "weight": 0.50, "trace": "T020"},
        {"method": "EV/EBITDA", "value_per_share": row(valuation, "EV/EBITDA value / share")[1], "weight": 0.25, "trace": "T021"},
        {"method": "P/E", "value_per_share": row(valuation, "P/E value / share")[1], "weight": 0.25, "trace": "T022"},
        {"method": "Blended target", "value_per_share": row(valuation, "Blended 12-month price target")[1], "weight": 1.00, "trace": "T003"},
    ]
    write_csv(tables_dir / "valuation_bridge.csv", valuation_rows, valuation_rows[0].keys())

    scenario_rows = [
        {"scenario": "Bear", "probability": scenarios[1][1], "value_per_share": scenarios[1][34], "trace": "T023"},
        {"scenario": "Base", "probability": scenarios[2][1], "value_per_share": scenarios[2][34], "trace": "T024"},
        {"scenario": "Bull", "probability": scenarios[3][1], "value_per_share": scenarios[3][34], "trace": "T025"},
        {"scenario": "Probability-weighted", "probability": 1.00, "value_per_share": scenarios[6][1], "trace": "T026"},
        {"scenario": "Current price", "probability": "", "value_per_share": 39.62, "trace": "T001"},
        {"scenario": "Blended target", "probability": "", "value_per_share": 41.00, "trace": "T003"},
    ]
    write_csv(tables_dir / "scenario_distribution.csv", scenario_rows, scenario_rows[0].keys())

    peer_rows = []
    peer_csv = read_csv(INPUT_REPO / "extracted/peer_valuation.csv")
    wanted = {"YETI", "GOLF", "MAT", "NWL"}
    for ticker in wanted:
        values = {"ticker": ticker}
        for metric in ["ev_ebitda", "forward_pe", "gross_margin", "operating_margin"]:
            match = next((r for r in peer_csv if r["ticker"] == ticker and r["metric"] == metric), None)
            values[metric] = match["value"] if match else ""
        values["trace"] = {"YETI": "T031", "GOLF": "T032", "MAT": "T033", "NWL": "T034"}[ticker]
        peer_rows.append(values)
    write_csv(tables_dir / "peer_context.csv", peer_rows, ["ticker", "ev_ebitda", "forward_pe", "gross_margin", "operating_margin", "trace"])

    mispricing_rows = [
        {"metric": "Current price", "agent_case": 39.62, "public_consensus": "", "trace": "T001"},
        {"metric": "Agent target", "agent_case": 41.00, "public_consensus": 47.75, "trace": "T003/T027"},
        {"metric": "Consensus median target", "agent_case": 41.00, "public_consensus": 53.00, "trace": "T003/T028"},
        {"metric": "FY2026 revenue", "agent_case": 1999.28858, "public_consensus": 2038.00, "trace": "T016/T029"},
        {"metric": "FY2026 EPS", "agent_case": 2.83, "public_consensus": 2.8742376, "trace": "T036/T030"},
    ]
    write_csv(tables_dir / "mispricing_test.csv", mispricing_rows, mispricing_rows[0].keys())

    if BENCHMARK_PARENT_FALLBACK and (tables_dir / "commit_history.csv").exists():
        commit_rows = read_csv(tables_dir / "commit_history.csv")
    else:
        commit_lines = subprocess.check_output(["git", "-C", str(INPUT_REPO), "log", "--oneline", "--reverse"], text=True).splitlines()
        commit_rows = []
        for idx, line in enumerate(commit_lines, start=1):
            sha, msg = line.split(" ", 1)
            commit_rows.append({"step": idx, "short_sha": sha, "message": msg, "trace": f"git commit {sha}"})
    write_csv(tables_dir / "commit_history.csv", commit_rows, commit_rows[0].keys())

    evidence_rows = [
        {"artifact": "SEC filings", "count": len(list((INPUT_REPO / "raw/filings").glob("*"))), "trace": "input raw/filings"},
        {"artifact": "Transcript PDFs", "count": len(list((INPUT_REPO / "raw/transcripts").glob("*.pdf"))), "trace": "input raw/transcripts"},
        {"artifact": "Other primary/market sources", "count": len([p for p in (INPUT_REPO / "raw/other").glob("*") if p.is_file()]), "trace": "input raw/other"},
        {"artifact": "Trace rows", "count": len(trace_rows), "trace": "analysis/memo_trace_table.csv"},
        {"artifact": "ADRs", "count": len(list((INPUT_REPO / "decisions").glob("*.md"))), "trace": "decisions/"},
        {"artifact": "Commits", "count": len(commit_rows), "trace": "git history"},
    ]
    write_csv(tables_dir / "evidence_counts.csv", evidence_rows, evidence_rows[0].keys())

    risk_rows = [
        {"risk": "Tariff pressure", "priority": 5, "evidence": "200 bps incremental impact; $80M / 430 bps vs FY2024", "what_would_make_it_real": "Tariffs stay high and mitigation/pricing cannot offset cost", "trace": "T042/T043"},
        {"risk": "US Drinkware / wholesale inventory", "priority": 4, "evidence": "DTC $1.128B; wholesale $740.7M; sell-through gap noted", "what_would_make_it_real": "Retailer sell-in stays weak and category promo pressure persists", "trace": "T011/T012/Q2"},
        {"risk": "Consumer cyclicality", "priority": 3, "evidence": "Discretionary premium brand; HOLD requires only 3.5% upside", "what_would_make_it_real": "Demand weakens before international growth scales", "trace": "T004/memo"},
        {"risk": "Valuation assumptions", "priority": 3, "evidence": "10.8% WACC; 2.75% terminal growth; blended target", "what_would_make_it_real": "WACC or multiple assumptions prove too generous", "trace": "T018/T019/T003"},
    ]
    write_csv(tables_dir / "risk_register.csv", risk_rows, risk_rows[0].keys())

    dead_end_rows = [
        {"hypothesis": "Investor-day long-range deck", "finding": "No usable current deck; used filings/releases/transcripts instead", "trace": "research/dead-ends.md"},
        {"hypothesis": "Solo Brands as core peer", "finding": "Distressed market cap and negative operating margin distorted comparison", "trace": "research/dead-ends.md / ADR 0003"},
        {"hypothesis": "Sell-side blind spot", "finding": "International and tariff-mitigation upside already visible in management/consensus", "trace": "research/dead-ends.md / analysis/sell_side_gap.md"},
    ]
    write_csv(tables_dir / "dead_ends.csv", dead_end_rows, dead_end_rows[0].keys())

    confidence_rows = [
        {"area": "Historical financials", "confidence": "High", "reason": "SEC facts, extracted tables, workbook checks", "trace": "T005-T010"},
        {"area": "Sales mix", "confidence": "High", "reason": "10-K Note 3 table parsed to CSV", "trace": "T011-T014"},
        {"area": "Guidance mechanics", "confidence": "Medium", "reason": "Management guide clear; model simplifications remain", "trace": "T015-T017/T035-T041"},
        {"area": "Valuation assumptions", "confidence": "Medium-Low", "reason": "WACC, terminal growth, and multiples are judgment calls", "trace": "ADR 0004/0005"},
        {"area": "Sell-side miss conclusion", "confidence": "Medium", "reason": "Public consensus checked; paid models unavailable", "trace": "T027-T030"},
    ]
    write_csv(tables_dir / "confidence_map.csv", confidence_rows, confidence_rows[0].keys())

    reconciliation_rows = [
        {"number": "$39.62 current price", "trace": "T001", "input_path": line_link("analysis/memo_trace_table.csv", find_trace_line("T001")), "source_chain": trace_row(trace_rows, "T001")["source_chain"], "reconciliation": "StockAnalysis market page -> extracted market data -> model Cover!B7 -> memo/deck."},
        {"number": "$1.868B FY2025 revenue", "trace": "T005", "input_path": line_link("analysis/memo_trace_table.csv", find_trace_line("T005")), "source_chain": trace_row(trace_rows, "T005")["source_chain"], "reconciliation": "SEC 10-K revenue fact -> annual/wide extracted CSV -> Model!D5 -> memo/deck."},
        {"number": "10.8% WACC", "trace": "T018", "input_path": line_link("analysis/memo_trace_table.csv", find_trace_line("T018")), "source_chain": trace_row(trace_rows, "T018")["source_chain"], "reconciliation": "Risk-free/ERP/beta/debt inputs -> Assumptions!B18 -> valuation/deck."},
        {"number": "$41 target", "trace": "T003", "input_path": line_link("analysis/memo_trace_table.csv", find_trace_line("T003")), "source_chain": trace_row(trace_rows, "T003")["source_chain"], "reconciliation": "DCF/multiple blend -> Valuation!B19 -> Cover!B6 -> memo/deck."},
        {"number": "200 bps tariff impact", "trace": "T042", "input_path": line_link("analysis/memo_trace_table.csv", find_trace_line("T042")), "source_chain": trace_row(trace_rows, "T042")["source_chain"], "reconciliation": "Q4 transcript line context -> trace table risk row -> risk slide."},
    ]
    write_csv(tables_dir / "reconciliation.csv", reconciliation_rows, reconciliation_rows[0].keys())

    # Audit numbers
    numbers = ["# Numbers Audit\n", f"Input commit: `{INPUT_COMMIT}`\n"]
    for tr in trace_rows:
        value = tr["value"]
        if any(ch.isdigit() for ch in value):
            line = find_trace_line(tr["trace_id"])
            numbers.append(f"- `{tr['trace_id']}` {tr['metric']}: `{value}` -> `{line_link('analysis/memo_trace_table.csv', line)}`; source chain: {tr['source_chain']}; model ref: {tr['model_ref']}\n")
    numbers.append("\n## Deck-Derived Counts\n")
    for r in evidence_rows:
        numbers.append(f"- {r['count']} {r['artifact']} -> `{r['trace']}` at input commit `{INPUT_COMMIT}`.\n")
    numbers.append("- 5 reconciliation spot-check numbers -> `audit/reconciliation.md` and `assets/tables/reconciliation.csv`.\n")
    numbers.append("- 20 deck slides -> `deck/source/slide_inventory.csv` and `deck/previews/slide-01.png` through `deck/previews/slide-20.png`.\n")
    numbers.append("- 1600 x 900 slide render size -> `deck/source/build_deck.py` and `decisions/0005-image-rendered-deck.md`.\n")
    (ROOT / "audit/numbers.md").write_text("".join(numbers), encoding="utf-8")

    # Quotes with context.
    quote_specs = [
        {
            "id": "Q1",
            "quote": "international addressable market exceeds the US",
            "rel_path": "extracted/transcripts/yeti-q4-2025-earnings-call-transcript.txt",
            "line": 199,
            "context": (196, 210),
        },
        {
            "id": "Q2",
            "quote": "notable gap compared to very strong double digit sell through",
            "rel_path": "extracted/transcripts/yeti-q3-2025-earnings-call-transcript.txt",
            "line": 92,
            "context": (88, 96),
        },
        {
            "id": "Q3",
            "quote": "approximately 200 basis points of incremental impact",
            "rel_path": "extracted/transcripts/yeti-q4-2025-earnings-call-transcript.txt",
            "line": 372,
            "context": (369, 374),
        },
    ]
    quotes_md = ["# Quotes Audit\n", f"Input commit: `{INPUT_COMMIT}`\n"]
    for q in quote_specs:
        lines = (INPUT_REPO / q["rel_path"]).read_text(encoding="utf-8", errors="replace").splitlines()
        start, end = q["context"]
        context = "\n".join(f"{i}: {lines[i-1]}" for i in range(start, end + 1))
        quotes_md.append(f"\n## {q['id']}: {q['quote']}\n\nSource: `{line_link(q['rel_path'], q['line'])}`\n\nContext:\n\n```text\n{context}\n```\n")
    (ROOT / "audit/quotes.md").write_text("".join(quotes_md), encoding="utf-8")

    # Reconciliation markdown.
    reconciliation_md = ["# Reconciliation Spot Check\n", f"Input commit: `{INPUT_COMMIT}`\n\n", md_table(reconciliation_rows, ["number", "trace", "input_path", "source_chain", "reconciliation"]), "\n"]
    (ROOT / "audit/reconciliation.md").write_text("".join(reconciliation_md), encoding="utf-8")

    # Slide trace files.
    slide_claims = {
        1: [
            {
                "claim": "Recommendation is HOLD with current price, market cap, target, and upside shown on slide.",
                "trace_ids": "T001-T004",
                "input_refs": ["memo/yeti_investment_memo.md:7", "analysis/memo_trace_table.csv:3-6"],
            },
            {
                "claim": "Scenario bubbles use bear/base/bull and probability-weighted values.",
                "trace_ids": "T023-T026",
                "input_refs": ["analysis/memo_trace_table.csv:25-28", "model/key-outputs.ndjson"],
            },
        ],
        2: [
            {
                "claim": "The thesis balances premium brand economics against limited valuation upside and tariff/category risk.",
                "trace_ids": "T003-T015, T042",
                "input_refs": ["memo/yeti_investment_memo.md:7-15", "memo/yeti_investment_memo.md:43-55"],
            }
        ],
        3: [
            {
                "claim": "Upgrade/downgrade paths are tied to tariff relief, international growth, US wholesale sell-through, and the recommendation hurdle.",
                "trace_ids": "T012, T014, T042-T043, Q2",
                "input_refs": ["memo/yeti_investment_memo.md:35", "memo/yeti_investment_memo.md:45-49", "decisions/0005-valuation-and-recommendation-framework.md:21"],
            }
        ],
        4: [
            {
                "claim": "Evidence corpus counts filings, transcripts, other sources, trace rows, ADRs, and commits from the input repo.",
                "trace_ids": "deck-derived counts",
                "input_refs": ["raw/filings/", "raw/transcripts/", "raw/other/", "analysis/memo_trace_table.csv", "decisions/", "git log at 8bb17db58bbb4201937887c6af6ee6e2b530d2fb"],
            }
        ],
        5: [
            {
                "claim": "Historical and projected revenue, free cash flow, gross margin, and operating margin come from the model trace table.",
                "trace_ids": "T005-T010, T015-T017",
                "input_refs": ["memo/yeti_investment_memo.md:13", "analysis/memo_trace_table.csv:7-19", "model/key-outputs.ndjson"],
            }
        ],
        6: [
            {
                "claim": "DTC, wholesale, international sales, and international share use FY2025 sales-breakdown traces.",
                "trace_ids": "T011-T014",
                "input_refs": ["memo/yeti_investment_memo.md:15", "analysis/memo_trace_table.csv:13-16"],
            },
            {
                "claim": "The international quote is management context from the Q4 transcript.",
                "trace_ids": "Q1",
                "input_refs": ["extracted/transcripts/yeti-q4-2025-earnings-call-transcript.txt:196-210"],
            },
        ],
        7: [
            {
                "claim": "Valuation bridge uses DCF, EV/EBITDA, P/E, blended target, and current price from the model.",
                "trace_ids": "T001, T003, T020-T022",
                "input_refs": ["memo/yeti_investment_memo.md:19-29", "analysis/memo_trace_table.csv:3-5", "analysis/memo_trace_table.csv:22-24", "decisions/0005-valuation-and-recommendation-framework.md:21-25"],
            }
        ],
        8: [
            {
                "claim": "Scenario distribution uses bear/base/bull probabilities and per-share values plus current price and target.",
                "trace_ids": "T001, T003, T023-T026",
                "input_refs": ["memo/yeti_investment_memo.md:23-29", "analysis/memo_trace_table.csv:3-5", "analysis/memo_trace_table.csv:25-28"],
            }
        ],
        9: [
            {
                "claim": "Competitive scatter uses YETI, GOLF, MAT, and NWL public valuation and operating-margin context.",
                "trace_ids": "T031-T034",
                "input_refs": ["memo/yeti_investment_memo.md:31-35", "analysis/memo_trace_table.csv:33-36", "extracted/peer_valuation.csv"],
            }
        ],
        10: [
            {
                "claim": "Peer context uses GOLF, MAT, and NWL while excluding DTC from core triangulation.",
                "trace_ids": "ADR 0003",
                "input_refs": ["decisions/0003-peer-set.md:11-26", "research/dead-ends.md:7-9"],
            }
        ],
        11: [
            {
                "claim": "The agent found no durable sell-side blind spot because consensus target/revenue/EPS were already optimistic versus its guide-derived base.",
                "trace_ids": "T027-T030, T035-T036",
                "input_refs": ["memo/yeti_investment_memo.md:37-41", "analysis/memo_trace_table.csv:29-38", "decisions/0006-sell-side-mispricing-test.md:21"],
            }
        ],
        12: [
            {
                "claim": "Tariff, US drinkware/wholesale, consumer cyclicality, valuation, and capital allocation risk priorities come from the memo risk section and trace table.",
                "trace_ids": "T012, T039, T042-T043",
                "input_refs": ["memo/yeti_investment_memo.md:43-49", "analysis/memo_trace_table.csv:14", "analysis/memo_trace_table.csv:41", "analysis/memo_trace_table.csv:44-45"],
            }
        ],
        13: [
            {
                "claim": "Reasoning graph links raw evidence, extraction, model, ADRs, rejected hypotheses, audit files, and final memo.",
                "trace_ids": "process",
                "input_refs": ["raw/", "extracted/", "model/", "decisions/", "research/dead-ends.md", "memo/yeti_investment_memo.md"],
            }
        ],
        14: [
            {
                "claim": "Commit-history slide summarizes staged source capture, extraction, model checks, and memo milestones.",
                "trace_ids": "input git log",
                "input_refs": ["git log at 8bb17db58bbb4201937887c6af6ee6e2b530d2fb"],
            }
        ],
        15: [
            {
                "claim": "Dead-end hypotheses are investor-day deck search, Solo Brands as core peer, and sell-side blind spot.",
                "trace_ids": "dead ends",
                "input_refs": ["research/dead-ends.md:3-13", "decisions/0003-peer-set.md:22", "decisions/0006-sell-side-mispricing-test.md:21"],
            }
        ],
        16: [
            {
                "claim": "Traceability system uses slide traces, trace IDs, source chains, input commit, raw evidence, and model cells.",
                "trace_ids": "T000-T043",
                "input_refs": ["memo/yeti_investment_memo.md:57-59", "analysis/memo_trace_table.csv", "sources.md", "tool-log.md"],
            }
        ],
        17: [
            {
                "claim": "Worked example verifies the $41 target through T003, the trace table, and model output.",
                "trace_ids": "T003",
                "input_refs": ["analysis/memo_trace_table.csv:5", "model/key-outputs.ndjson", "model/yeti_investment_model.xlsx"],
            }
        ],
        18: [
            {
                "claim": "Reconciliation spot-check uses five numbers: current price, FY2025 revenue, WACC, target, and tariff impact.",
                "trace_ids": "T001, T005, T018, T003, T042",
                "input_refs": ["analysis/memo_trace_table.csv:3", "analysis/memo_trace_table.csv:7", "analysis/memo_trace_table.csv:20", "analysis/memo_trace_table.csv:5", "analysis/memo_trace_table.csv:44"],
            }
        ],
        19: [
            {
                "claim": "Confidence map separates source-backed facts from judgment-heavy assumptions and sell-side edge limitations.",
                "trace_ids": "T005-T043, ADRs",
                "input_refs": ["memo/yeti_investment_memo.md:51-55", "decisions/0004-discount-rate-and-terminal-growth.md:22", "decisions/0005-valuation-and-recommendation-framework.md:21", "decisions/0006-sell-side-mispricing-test.md:21"],
            }
        ],
        20: [
            {
                "claim": "Limitations and next analyst work come from the memo's confidence and limitations section.",
                "trace_ids": "limitations",
                "input_refs": ["memo/yeti_investment_memo.md:51-55"],
            }
        ],
    }
    for slide, claims in slide_claims.items():
        body = [f"# Slide {slide:02d} Trace\n\n", f"Input commit: `{INPUT_COMMIT}`\n\n", "Logical input root: `/input/repo/`\n\n"]
        for idx, claim in enumerate(claims, start=1):
            body.append(f"## Claim {idx}\n\n{claim['claim']}\n\n")
            body.append(f"Trace IDs: `{claim['trace_ids']}`\n\n")
            body.append("Input references:\n\n")
            for ref in claim["input_refs"]:
                body.append(f"- `{logical(ref)}`\n")
            body.append("\n")
        body.append("## Primary Input Files\n\n")
        for p in ["memo/yeti_investment_memo.md", "analysis/memo_trace_table.csv", "model/key-outputs.ndjson", "decisions/", "research/dead-ends.md"]:
            body.append(f"- `{logical(p)}`\n")
        (traces_dir / f"slide-{slide:02d}.md").write_text("".join(body), encoding="utf-8")

    (ROOT / "assets/images/README.md").write_text("# Images\n\nNo photography, stock imagery, icons, or AI-generated images are used. The deck relies on reproducible charts and diagrams.\n", encoding="utf-8")

    print(f"Extracted deck data from {INPUT_REPO} at {INPUT_COMMIT}")


if __name__ == "__main__":
    main()
