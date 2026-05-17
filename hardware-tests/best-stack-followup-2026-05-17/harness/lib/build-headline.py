#!/usr/bin/env python3
"""Build the headline CSV for the best-stack follow-up bundle.

Reads every cell.json under <bundle>/<host>/<model>/<backend>/ctx*/cell.json
and emits one row per (host, model, backend) with peak metrics across the
conc=1 cells.

This bundle's claim scope is single-user (conc=1). Multi-user is out of scope.
"""
import argparse, csv, json
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bundle", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()

    rows = []
    for host_dir in sorted(args.bundle.iterdir()):
        if not host_dir.is_dir() or host_dir.name in {"harness", "aggregate", "workloads"}:
            continue
        for model_dir in sorted(host_dir.iterdir()):
            if not model_dir.is_dir():
                continue
            for backend_dir in sorted(model_dir.iterdir()):
                if not backend_dir.is_dir():
                    continue
                cells = []
                for cell_dir in sorted(backend_dir.iterdir()):
                    cj = cell_dir / "cell.json"
                    if not cj.exists():
                        continue
                    c = json.loads(cj.read_text())
                    if c.get("conc") != 1:
                        continue
                    ps = c.get("per_slot") or {}
                    if ps.get("decode_tps_mean") is None:
                        continue
                    cells.append((cell_dir.name, c, ps))
                if not cells:
                    continue
                best_dec = max(cells, key=lambda x: x[2]["decode_tps_mean"])
                best_pre = max(cells, key=lambda x: (x[2].get("prefill_tps_mean") or 0))
                ctx16k = [c for c in cells if c[1]["ctx"] == 16384]
                ctx16k_decode = ctx16k[0][2]["decode_tps_mean"] if ctx16k else None
                ctx16k_decode_sd = ctx16k[0][2].get("decode_tps_sd") if ctx16k else None
                ctx16k_ttft = ctx16k[0][2].get("ttft_ms_mean") if ctx16k else None
                rows.append({
                    "host": host_dir.name,
                    "model": model_dir.name,
                    "backend": backend_dir.name,
                    "cells_present_conc1": len(cells),
                    "peak_prefill_tps":     round(best_pre[2].get("prefill_tps_mean") or 0, 3),
                    "at_cell_prefill":      best_pre[0],
                    "peak_decode_tps":      round(best_dec[2]["decode_tps_mean"], 3),
                    "peak_decode_tps_sd":   round(best_dec[2].get("decode_tps_sd") or 0, 4),
                    "at_cell_decode":       best_dec[0],
                    "decode_tps_at_ctx16k":     round(ctx16k_decode, 3) if ctx16k_decode is not None else "",
                    "decode_tps_at_ctx16k_sd":  round(ctx16k_decode_sd, 4) if ctx16k_decode_sd is not None else "",
                    "ttft_ms_at_ctx16k":        round(ctx16k_ttft, 0) if ctx16k_ttft is not None else "",
                    "engine":                   best_dec[1].get("engine", ""),
                })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as f:
        if rows:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), quoting=csv.QUOTE_NONNUMERIC)
            w.writeheader()
            w.writerows(rows)
    print(f"wrote {len(rows)} rows -> {args.out}")


if __name__ == "__main__":
    main()
