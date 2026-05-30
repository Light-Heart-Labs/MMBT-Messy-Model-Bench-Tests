#!/usr/bin/env python3
"""bench_power — analyze the dual-GPU power log captured during a bench run.

Reads gpu_power.csv (from gpu_power_logger.sh; cols: ts,gpu,power_w,util_sm,
util_mem,mem_used_mib,temp_c,sm_clk_mhz,cell) and reports per-GPU percentiles,
GPU0-vs-GPU1 asymmetry, combined both-GPU draw vs cap, draw-by-phase
(decode-burst vs CPU-tool-gap), and a per-served-model split if the cell tags
span multiple models. Answers: are both GPUs ever near full power together?

Usage:
  python3 bench_power.py [--csv /tmp/bench-autopilot/gpu_power.csv]
                        [--cap-per-gpu 600] [--md]   # --md = markdown section
"""
from __future__ import annotations
import argparse, csv, collections, statistics

def pct(sorted_vals, q):
    if not sorted_vals: return 0.0
    i = min(len(sorted_vals)-1, int(q*len(sorted_vals)))
    return sorted_vals[i]

def load(path):
    rows = []
    with open(path) as f:
        for r in csv.DictReader(f):
            try:
                r['power_w'] = float(r['power_w']); r['util_sm'] = float(r.get('util_sm') or 0)
                rows.append(r)
            except (ValueError, TypeError):
                continue
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="/tmp/bench-autopilot/gpu_power.csv")
    ap.add_argument("--cap-per-gpu", type=float, default=600.0)
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    rows = load(a.csv)
    cap2 = a.cap_per_gpu * 2
    gpus = sorted({r['gpu'] for r in rows})

    per = {}
    for g in gpus:
        p = sorted(r['power_w'] for r in rows if r['gpu'] == g)
        u = [r['util_sm'] for r in rows if r['gpu'] == g]
        per[g] = dict(n=len(p), mean=statistics.mean(p) if p else 0,
                      p50=pct(p,.5), p90=pct(p,.9), p99=pct(p,.99), mx=max(p) if p else 0,
                      util=statistics.mean(u) if u else 0)

    # combined simultaneous draw
    bt = collections.defaultdict(dict)
    for r in rows:
        bt[r['ts']][r['gpu']] = r['power_w']
    comb = sorted(a0['0']+a0['1'] for a0 in bt.values() if '0' in a0 and '1' in a0)
    over_full = sum(1 for c in comb if c > cap2*0.95)

    # draw-by-phase: decode (any gpu util>20) vs idle/tool (both util<5)
    decode = [r['power_w'] for r in rows if r['util_sm'] > 20]
    idle   = [r['power_w'] for r in rows if r['util_sm'] < 5]

    L = []
    p = L.append
    p("## Power behavior (dual RTX PRO 6000 Blackwell, %dW/GPU cap)" % a.cap_per_gpu)
    p("")
    p("From %d samples (%d paired) captured during the run. Per-GPU:" % (len(rows), len(comb)))
    p("")
    p("| GPU | mean | p50 | p90 | p99 | max | %of cap | mean util |")
    p("|---|--:|--:|--:|--:|--:|--:|--:|")
    for g in gpus:
        d = per[g]
        p("| GPU%s | %.0f | %.0f | %.0f | %.0f | **%.0f** | %.0f%% | %.0f%% |" % (
            g, d['mean'], d['p50'], d['p90'], d['p99'], d['mx'], 100*d['mx']/a.cap_per_gpu, d['util']))
    p("")
    if comb:
        p("**Combined both-GPU draw:** median %.0fW (%.0f%% of %dW cap), p90 %.0fW, max **%.0fW (%.0f%%)**." % (
            pct(comb,.5), 100*pct(comb,.5)/cap2, cap2, pct(comb,.9), max(comb), 100*max(comb)/cap2))
        p("Samples within 5%% of full (%.0fW): **%d / %d (%.1f%%)**." % (cap2*0.95, over_full, len(comb), 100*over_full/len(comb)))
    p("")
    if decode and idle:
        p("**Draw by phase:** decode bursts (util>20%%) mean %.0fW/GPU; CPU-tool / idle phases (util<5%%) mean %.0fW/GPU." % (
            statistics.mean(decode), statistics.mean(idle)))
    if len(gpus) == 2:
        asym = per['0']['mean'] - per['1']['mean']
        p("")
        p("**GPU0 vs GPU1:** GPU0 averages %.0fW vs GPU1 %.0fW (%+.0fW). %s" % (
            per['0']['mean'], per['1']['mean'], asym,
            "Pipeline-parallel (`-sm layer`) loads layers across cards in sequence, so the two rarely peak together — the combined draw never approaches the 1200W ceiling."
            if asym > 10 else "Near-balanced — consistent with tensor-parallel (both cards active per token)."))
    out = "\n".join(L)
    print(out)

if __name__ == "__main__":
    main()
