#!/usr/bin/env python3
"""Backfill missing MMBT-canonical fields in already-written cell.json files.

Idempotent. Won't overwrite existing fields. Reads inferences.jsonl/batches.jsonl
to fill in computable fields (aggregate medians, cold_start expansions).
"""
import argparse, json
from pathlib import Path
from statistics import median, mean


def backfill_cell(cell_dir, default_engine=None):
    cj = cell_dir / "cell.json"
    if not cj.exists():
        return
    c = json.loads(cj.read_text())

    if "seed" not in c:
        c["seed"] = 42  # all our runs use temperature=0 seed=42
    if "started" not in c:
        try:
            stat = cj.stat()
            import datetime
            c["started"] = datetime.datetime.fromtimestamp(stat.st_mtime, datetime.timezone.utc).isoformat()
        except Exception:
            pass
    if "inferences_path" not in c:
        c["inferences_path"] = "inferences.jsonl"
    if "batches_path" not in c:
        c["batches_path"] = "batches.jsonl"
    if "engine" not in c and default_engine:
        c["engine"] = default_engine

    # Aggregate block
    agg = c.setdefault("aggregate", {})
    batches_path = cell_dir / "batches.jsonl"
    if batches_path.exists():
        bats = [json.loads(l) for l in batches_path.read_text().splitlines() if l.strip()]
        warmup = c.get("warmup_batches", 0)
        body = bats[warmup:]
        agg.setdefault("n_batches_total", len(bats))
        agg.setdefault("n_batches_body",  len(body))
        agg_body_vals = [b.get("aggregate_decode_tps", 0) for b in body]
        if agg_body_vals and "aggregate_decode_tps_mean" not in agg:
            agg["aggregate_decode_tps_mean"] = mean(agg_body_vals)
        if agg_body_vals and "aggregate_decode_tps_median" not in agg:
            agg["aggregate_decode_tps_median"] = median(agg_body_vals)

    # Expand cold_start if minimal
    cs = c.get("cold_start") or {}
    if cs and batches_path.exists():
        bats = [json.loads(l) for l in batches_path.read_text().splitlines() if l.strip()]
        if bats:
            b0 = bats[0]
            cs.setdefault("aggregate_decode_tps",      b0.get("aggregate_decode_tps"))
            cs.setdefault("per_slot_decode_tps_mean",  b0.get("per_slot_decode_tps_mean"))
            cs.setdefault("wall_s",                    b0.get("wall_s"))
    c["cold_start"] = cs

    cj.write_text(json.dumps(c, indent=2))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True, help="Directory containing per-cell subdirs")
    p.add_argument("--engine", default=None, help="Engine label to set if missing")
    args = p.parse_args()
    root = Path(args.root)
    for sub in sorted(root.iterdir()):
        if sub.is_dir() and (sub / "cell.json").exists():
            backfill_cell(sub, default_engine=args.engine)
            print(f"backfilled {sub.name}")


if __name__ == "__main__":
    main()
