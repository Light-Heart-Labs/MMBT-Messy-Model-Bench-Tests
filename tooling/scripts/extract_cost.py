#!/usr/bin/env python3
"""Extract cost / throughput metrics from a run's receipt + transcript.

Writes a cost.json sibling to receipt.json and summary.json. Pure post-hoc;
does not need access to the live run.

Usage:
    extract_cost.py <run_dir>            # one run
    extract_cost.py --all                # all runs under agent-pilot/logs/

Cost estimates are upper-bound approximations:
- Wall time × power.limit gives "if the GPU were drawing at its cap the entire
  run, this is the energy" — real draw is lower (idle between calls, peaks
  during decode).
- Future runs should use a sidecar nvidia-smi sampler for truthful power.
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


LOCAL_KWH_RATE_USD = 0.13  # rough US residential default; configurable


def parse_iso(ts: str) -> float:
    """Parse ISO 8601 with timezone. Returns Unix epoch seconds."""
    return datetime.fromisoformat(ts).timestamp()


def parse_nvidia_smi_line(line: str) -> dict:
    """Parse one line of nvidia-smi --query-gpu=... csv,noheader output.

    Format (per launch-commands.md):
      index, name, driver_version, power.limit, power.draw, temperature.gpu,
      memory.used, memory.total, clocks.current.graphics
    """
    parts = [p.strip() for p in line.split(",")]
    if len(parts) < 9:
        return {}
    def num(s):
        m = re.search(r"[\d.]+", s)
        return float(m.group()) if m else None
    return {
        "index": parts[0],
        "name": parts[1],
        "power_limit_w": num(parts[3]),
        "power_draw_w_at_start": num(parts[4]),
        "memory_used_mib": num(parts[6]),
        "memory_total_mib": num(parts[7]),
    }


def find_first_match(transcript, pattern, where="command"):
    """Return (iter, t) of the first tool call matching pattern, or (None, None)."""
    for entry in transcript:
        if entry.get("type") != "tool":
            continue
        if where == "command":
            cmd = entry.get("args", {}).get("command", "") or ""
            if pattern in cmd:
                return entry.get("iter"), parse_iso(entry["t"])
        elif where == "name":
            if entry.get("name") == pattern:
                return entry.get("iter"), parse_iso(entry["t"])
    return None, None


def extract(run_dir: Path) -> dict:
    receipt_path = run_dir / "receipt.json"
    transcript_path = run_dir / "transcript.jsonl"
    summary_path = run_dir / "summary.json"

    if not receipt_path.exists() or not transcript_path.exists():
        return {"error": f"missing receipt or transcript in {run_dir}", "run_dir": str(run_dir)}

    receipt = json.loads(receipt_path.read_text())
    transcript = []
    for ln, line in enumerate(transcript_path.read_text().splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            transcript.append(json.loads(line))
        except json.JSONDecodeError:
            # Skip malformed lines — usually a partially-flushed line at the
            # end if the harness was killed mid-write. Quiet skip rather than
            # blowing up the whole run's extraction.
            pass
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else None

    # Find run-relevant GPU. Match the GPU index used by vLLM if we can.
    gpu_lines = (receipt.get("hardware", {}) or {}).get("nvidia_smi", [])
    gpu_info_per = [parse_nvidia_smi_line(l) for l in gpu_lines]
    gpu_info_per = [g for g in gpu_info_per if g]

    # Heuristic: pick the GPU with the highest memory_used at start (the one
    # vLLM allocated against). Fallback to GPU 0.
    if gpu_info_per:
        gpu = max(gpu_info_per, key=lambda g: g.get("memory_used_mib") or 0)
    else:
        gpu = {}

    # Tokens: sum across model turns (more accurate than relying on summary)
    model_turns = [e for e in transcript if e.get("type") == "model"]
    total_completion = sum(e.get("completion_tokens", 0) or 0 for e in model_turns)
    total_prompt = sum(e.get("prompt_tokens", 0) or 0 for e in model_turns)
    total_tokens = total_completion + total_prompt

    model_call_wall = sum(e.get("wall_s", 0) or 0 for e in model_turns)
    tool_turns = [e for e in transcript if e.get("type") == "tool"]
    tool_call_wall = sum(e.get("wall_s", 0) or 0 for e in tool_turns)

    # Wall: prefer summary.json's elapsed_s; fall back to first/last transcript timestamps.
    if summary and "elapsed_s" in summary:
        wall_s = summary["elapsed_s"]
    elif transcript:
        wall_s = parse_iso(transcript[-1]["t"]) - parse_iso(transcript[0]["t"])
    else:
        wall_s = None

    started_at = parse_iso(transcript[0]["t"]) if transcript else None
    iters = max((e.get("iter", 0) or 0) for e in transcript) if transcript else 0

    # Time-to-X markers (relative to run start)
    def tts(it_t):
        return round(it_t - started_at, 1) if (it_t and started_at) else None

    write_iter, write_t = find_first_match(transcript, "write_file", where="name")
    if write_t is None:  # also count bash redirects to /workspace/...
        for e in tool_turns:
            cmd = e.get("args", {}).get("command", "") or ""
            if re.search(r">\s*/workspace/\S", cmd) or "tee /workspace/" in cmd:
                write_iter = e.get("iter"); write_t = parse_iso(e["t"])
                break
    commit_iter, commit_t = find_first_match(transcript, "git commit", where="command")
    tag_iter, tag_t = find_first_match(transcript, "git tag", where="command")

    # Throughput
    completion_tps_avg = round(total_completion / model_call_wall, 1) if model_call_wall > 0 else None

    # Energy / cost approximation
    power_limit_w = gpu.get("power_limit_w")
    est_kwh_upper_bound = None
    est_cost_usd_upper_bound = None
    if power_limit_w and wall_s:
        est_kwh_upper_bound = round(power_limit_w * wall_s / 3600.0 / 1000.0, 4)
        est_cost_usd_upper_bound = round(est_kwh_upper_bound * LOCAL_KWH_RATE_USD, 4)

    out = {
        "run_name": receipt.get("run_name"),
        "model": receipt.get("vllm", {}).get("served_model_name"),
        "wall_s": wall_s,
        "iters": iters,
        "tokens": {
            "completion_total": total_completion,
            "prompt_total": total_prompt,
            "all_total": total_tokens,
        },
        "throughput": {
            "completion_tps_avg": completion_tps_avg,
            "model_call_wall_s": round(model_call_wall, 1),
            "tool_call_wall_s": round(tool_call_wall, 1),
            "_note": "completion_tps is over model-API call time only, not wall (tool execution + sandbox not counted)",
        },
        "time_to": {
            "first_write_s": tts(write_t),
            "first_commit_s": tts(commit_t),
            "first_tag_s": tts(tag_t),
        },
        "gpu": {
            "name": gpu.get("name"),
            "power_limit_w": power_limit_w,
            "power_draw_w_at_start": gpu.get("power_draw_w_at_start"),
            "memory_used_mib_at_start": gpu.get("memory_used_mib"),
            "memory_total_mib": gpu.get("memory_total_mib"),
            "_note": "power and memory captured at run START only; real values vary during the run. For truthful power, future runs need a sidecar nvidia-smi sampler.",
        },
        "energy_estimate": {
            "kwh_upper_bound": est_kwh_upper_bound,
            "cost_usd_upper_bound": est_cost_usd_upper_bound,
            "rate_usd_per_kwh": LOCAL_KWH_RATE_USD,
            "_note": "Upper bound: assumes GPU drew at power.limit for the entire wall time. Real draw is lower (idle between calls, peaks during decode). Treat as ceiling, not point estimate.",
        },
    }
    return out


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Layouts:\n"
            "  Source-bench layout (private working repo): logs live at\n"
            "    <bench-root>/agent-pilot/logs/<run_name>/. Run from anywhere\n"
            "    with --all (uses the script's own location to find logs).\n"
            "  MMBT public layout: per-entry receipt + transcript live at\n"
            "    benchmarks/<task>/<model>/. Run on a single entry with\n"
            "    `extract_cost.py benchmarks/<task>/<model>/`. The cost.json\n"
            "    files for the published entries are already committed; this\n"
            "    script is for fresh local runs or for re-deriving cost.json\n"
            "    after harness or transcript changes.\n"
        ),
    )
    ap.add_argument("run_dir", nargs="?", help="path to a single run dir (any layout)")
    ap.add_argument("--all", action="store_true", help="run on every dir under --logs-dir")
    ap.add_argument(
        "--logs-dir", default=None,
        help="for --all: directory containing run-name subdirs. "
             "Default: <script>/../logs/ (works from a source-bench layout where "
             "scripts/ is sibling to logs/). In an MMBT clone the default doesn't "
             "exist — pass an explicit path or use single-run mode against an entry.",
    )
    args = ap.parse_args()

    if args.all:
        if args.logs_dir:
            logs_dir = Path(args.logs_dir).resolve()
        else:
            logs_dir = (Path(__file__).resolve().parent.parent / "logs").resolve()
        if not logs_dir.is_dir():
            ap.error(
                f"--all expected a logs directory at {logs_dir} (none found). "
                f"Pass --logs-dir <path> if your logs live elsewhere, or use single-run mode: "
                f"`extract_cost.py <run_dir>`. In an MMBT clone, the per-entry cost.json "
                f"files are already committed at benchmarks/<task>/<model>/cost.json — "
                f"this script is for re-deriving them or for fresh local runs."
            )
        run_dirs = sorted([d for d in logs_dir.iterdir() if d.is_dir()])
    elif args.run_dir:
        run_dirs = [Path(args.run_dir)]
    else:
        ap.error("provide a run_dir or --all")

    for d in run_dirs:
        out = extract(d)
        if "error" in out:
            print(f"SKIP  {d.name}: {out['error']}", file=sys.stderr)
            continue
        out_path = d / "cost.json"
        out_path.write_text(json.dumps(out, indent=2))
        wall = out.get("wall_s") or 0
        ctok = out["tokens"]["completion_total"]
        cost = out["energy_estimate"]["cost_usd_upper_bound"]
        ttw = out["time_to"]["first_write_s"]
        tag_t = out["time_to"]["first_tag_s"]
        print(f"OK    {d.name:35s}  wall={wall:>5.0f}s  ctok={ctok:>6d}  ttw={ttw}  ttag={tag_t}  cost_upper=${cost}")


if __name__ == "__main__":
    main()
