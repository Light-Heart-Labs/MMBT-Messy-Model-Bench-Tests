#!/usr/bin/env python3
"""bench_autopilot_enriched — self-healing supervisor for the MMBT microbench (enriched).

Enriched fork of bench_autopilot.py. Preserves ALL original behavior, CLI flags,
and status.json keys (additive-only), and layers on:

  1) Pushover notifications  — per-arm completion, endpoint restart, run done/incomplete.
  2) Per-cell timing + tok/s  — parse each cell's summary.json/transcript for wall_s +
     completion_tokens; record per-arm median cell wall + median tok/s into status.json.
  3) Richer status.json       — adds eta_secs, recent_cells, fails, started_at, elapsed_secs.
  4) Resume-safety            — per-loop heartbeat ts; abort on start if a previous
     autopilot heartbeat is fresh (<120s) to prevent double-drive.
  5) --once flag              — single status write + exit (for external monitors).

The live run uses bench_autopilot.py; this file is a NEW filename so it can be
swapped in for the next run without disturbing the current one. status.json schema
is backward-compatible: only new keys/flags are added.

Usage:
  python3 bench_autopilot_enriched.py --target-n 20 [--config bench_autopilot.config.json]
  python3 bench_autopilot_enriched.py --once          # write status snapshot + exit
"""
from __future__ import annotations
import argparse, json, os, signal, statistics, subprocess, sys, time
from pathlib import Path

HOME = Path(os.path.expanduser("~"))
BENCH = HOME / "bench"
LOGS = BENCH / "logs"
TOOLING = BENCH / "tooling"
SCRIPTS = TOOLING / "scripts"
STATE_DIR = Path("/tmp/bench-autopilot")
STATE_DIR.mkdir(parents=True, exist_ok=True)
STATUS = STATE_DIR / "status.json"
LOG = STATE_DIR / "autopilot.log"
HEARTBEAT = STATE_DIR / "heartbeat.json"        # enrichment 4: resume-safety
NOTIFY_SH = HOME / "dream-fleet-test" / "lib" / "notify.sh"

HEARTBEAT_FRESH_SECS = 120                       # abort if prior heartbeat newer than this

TASKS = ["p1_bugfix","p1_testwrite","p1_refactor","p2_extract","p2_ci",
         "p2_hallucination","p2_triage","p3_doc","p3_business","p3_market",
         "p3_writing","p3_pm"]

DEFAULT_CONFIG = {
    "model": "qwen3.5-397b-a17b",
    "port": 8001,
    "max_model_len": 131072,
    "ctx_size": 131072,
    "gguf": "/models/unsloth-Qwen3.5-397B-A17B-GGUF/UD-Q3_K_XL/Qwen3.5-397B-A17B-UD-Q3_K_XL-00001-of-00005.gguf",
    "container": "llama-397b",
    "image": "ghcr.io/ggml-org/llama.cpp:server-cuda-b9014",
    "arms": [{"label": "397b-nothink", "thinking": "off"},
             {"label": "397b-think",   "thinking": "on"}],
    "stuck_secs": 1200,        # transcript frozen this long = truly hung (kill it)
    "endpoint_grace_secs": 180 # endpoint must load within this on (re)launch
}


def log(msg: str):
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def sh(cmd, **kw):
    return subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, **kw)


# --- enrichment 1: pushover -------------------------------------------------
def notify(title: str, msg: str, priority: int = 0):
    """Best-effort Pushover via the fleet notify.sh helper. Never raises."""
    try:
        if not NOTIFY_SH.exists():
            return
        cmd = f'source "{NOTIFY_SH}" && notify_push "$1" "$2" "$3"'
        subprocess.run(["bash", "-c", cmd, "_", title, msg, str(priority)],
                       capture_output=True, text=True, timeout=20)
    except Exception as e:
        log(f"notify failed (non-fatal): {e}")


# --- enrichment 4: heartbeat / resume-safety --------------------------------
def write_heartbeat():
    try:
        HEARTBEAT.write_text(json.dumps({
            "pid": os.getpid(),
            "ts": time.time(),
            "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }))
    except Exception:
        pass


def fresh_heartbeat():
    """Return (age_secs, pid) if a foreign heartbeat is fresher than the threshold, else None."""
    try:
        hb = json.loads(HEARTBEAT.read_text())
    except Exception:
        return None
    pid = hb.get("pid")
    if pid == os.getpid():
        return None
    age = time.time() - float(hb.get("ts", 0))
    if age < HEARTBEAT_FRESH_SECS:
        return (age, pid)
    return None


def endpoint_up(port: int) -> bool:
    r = sh(f"curl -sf http://127.0.0.1:{port}/v1/models")
    return r.returncode == 0


def container_running(name: str) -> bool:
    r = sh(["docker", "ps", "--format", "{{.Names}}"])
    return name in r.stdout.split()


def ensure_endpoint(cfg: dict) -> bool:
    port, name = cfg["port"], cfg["container"]
    if endpoint_up(port):
        return True
    log(f"endpoint down — (re)launching {name}")
    notify("bench: endpoint restart", f"{name} down — relaunching on port {port}", 0)  # enrichment 1
    sh(["docker", "rm", "-f", name])
    sh(["docker", "run", "-d", "--name", name, "--gpus", "all", "--shm-size", "16g",
        "-v", f"{HOME}/models:/models:ro", "-p", f"127.0.0.1:{port}:8000",
        cfg["image"], "-m", cfg["gguf"], "-a", cfg["model"],
        "-ngl", "999", "-sm", "layer", "-fa", "on", "-c", str(cfg["ctx_size"]),
        "-b", "2048", "-np", "1", "--jinja", "--reasoning-format", "none",
        "--host", "0.0.0.0", "--port", "8000"])
    for _ in range(cfg["endpoint_grace_secs"] // 5):
        if endpoint_up(port):
            log("endpoint back up")
            return True
        if not container_running(name):
            log("ERROR: endpoint container died during load");
            log((sh(["docker","logs","--tail","15",name]).stdout or "")[-800:])
            notify("bench: endpoint FAILED", f"{name} died during model load", 1)  # enrichment 1
            return False
        time.sleep(5)
    log("ERROR: endpoint did not come up within grace period")
    notify("bench: endpoint FAILED", f"{name} did not load within grace period", 1)  # enrichment 1
    return False


def cell_done(run_name: str) -> bool:
    d = LOGS / run_name
    return (d / "summary.json").exists() and (d / "workspace_final.tar.gz").exists()


def cell_verdict(run_name: str):
    g = LOGS / run_name / "grade.json"
    if not g.exists():
        return None
    try:
        v = json.loads(g.read_text()).get("verdict")
        return v
    except Exception:
        return "BAD_GRADE"


# --- enrichment 2: per-cell timing + tok/s ----------------------------------
def cell_metrics(run_name: str):
    """Return (wall_s, tok_ps) for a completed cell, from summary.json (transcript fallback).

    tok/s = total_completion_tokens / elapsed_s. Returns (None, None) if unavailable.
    """
    d = LOGS / run_name
    wall = toks = None
    sp = d / "summary.json"
    if sp.exists():
        try:
            s = json.loads(sp.read_text())
            wall = s.get("elapsed_s")
            toks = s.get("total_completion_tokens")
        except Exception:
            pass
    # transcript fallback: sum per-iter completion_tokens, last t - first t for wall
    if (wall is None or toks is None) and (d / "transcript.jsonl").exists():
        try:
            rows = [json.loads(l) for l in (d / "transcript.jsonl").read_text().splitlines() if l.strip()]
            ct = [r.get("completion_tokens") for r in rows if isinstance(r.get("completion_tokens"), (int, float))]
            if toks is None and ct:
                toks = sum(ct)
            ws = [r.get("wall_s") for r in rows if isinstance(r.get("wall_s"), (int, float))]
            if wall is None and ws:
                wall = sum(ws)
        except Exception:
            pass
    tok_ps = None
    if isinstance(wall, (int, float)) and wall > 0 and isinstance(toks, (int, float)):
        tok_ps = round(toks / wall, 2)
    return (wall if isinstance(wall, (int, float)) else None, tok_ps)


def arm_progress(label: str, target: int):
    """Return (done, total, per_task_counts, metrics) for an arm up to target N.

    metrics (enrichment 2): {'wall_median', 'tok_ps_median', 'n_timed'} for done cells.
    """
    total = len(TASKS) * target
    done = 0
    pertask = {}
    walls = []
    tokps = []
    for t in TASKS:
        c = 0
        passes = 0
        for v in range(1, target + 1):
            rn = f"{t}_{label}_v{v}"
            if cell_done(rn):
                c += 1; done += 1
                if cell_verdict(rn) in ("PASS", "STRUCTURAL_PASS"):
                    passes += 1
                w, tp = cell_metrics(rn)
                if w is not None:
                    walls.append(w)
                if tp is not None:
                    tokps.append(tp)
        pertask[t] = {"done": c, "pass": passes}
    metrics = {
        "wall_median": round(statistics.median(walls), 1) if walls else None,
        "tok_ps_median": round(statistics.median(tokps), 2) if tokps else None,
        "n_timed": len(walls),
    }
    return done, total, pertask, metrics


def newest_transcript():
    best = None; best_mt = 0
    for d in LOGS.glob("p*_397b-*_v*"):
        tp = d / "transcript.jsonl"
        if tp.exists():
            mt = tp.stat().st_mtime
            if mt > best_mt:
                best_mt = mt; best = tp
    return best, best_mt


def current_cell_info():
    tp, mt = newest_transcript()
    if not tp:
        return {"cell": None, "iter": None, "frozen_secs": None}
    it = None
    try:
        last = None
        for line in tp.read_text().splitlines():
            last = line
        if last:
            it = json.loads(last).get("iter")
    except Exception:
        pass
    return {"cell": tp.parent.name, "iter": it, "frozen_secs": int(time.time() - mt)}


def kill_stuck(cell: str):
    """Kill a truly-hung cell's harness PID + sandbox so the chain advances."""
    log(f"STUCK: killing hung cell {cell}")
    r = sh(["pgrep", "-f", f"harness.py {cell} "])
    for pid in r.stdout.split():
        sh(["kill", "-TERM", pid])
    time.sleep(3)
    r = sh(["pgrep", "-f", f"harness.py {cell} "])
    for pid in r.stdout.split():
        sh(["kill", "-KILL", pid])
    sh(["docker", "rm", "-f", f"bench-sandbox-{cell}"])


# --- enrichment 3: recent cells + fails -------------------------------------
def recent_cells_and_fails(limit: int = 8):
    """Last ~`limit` completed cells (by summary mtime) with wall+verdict, plus all failed run_names."""
    sums = sorted(LOGS.glob("p*_397b-*_v*/summary.json"), key=lambda p: p.stat().st_mtime)
    recent = []
    for sp in sums[-limit:]:
        rn = sp.parent.name
        w, tp = cell_metrics(rn)
        recent.append({
            "run": rn,
            "verdict": cell_verdict(rn),
            "wall_s": w,
            "tok_ps": tp,
            "finished": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(sp.stat().st_mtime)),
        })
    recent.reverse()  # newest first
    fails = []
    for sp in sums:
        rn = sp.parent.name
        v = cell_verdict(rn)
        if v is not None and v not in ("PASS", "STRUCTURAL_PASS"):
            fails.append(rn)
    return recent, fails


def write_status(cfg, target, phase, arms_done, started_at=None):
    arms = []
    grand_done = grand_total = 0
    all_walls = []
    for a in cfg["arms"]:
        done, total, pertask, metrics = arm_progress(a["label"], target)
        grand_done += done; grand_total += total
        if metrics["wall_median"] is not None:
            all_walls.append(metrics["wall_median"])
        arms.append({"label": a["label"], "done": done, "total": total,
                     "pertask": pertask, "metrics": metrics})  # metrics: enrichment 2
    cur = current_cell_info()
    # enrichment 3: eta_secs from median cell wall * remaining cells
    rem = grand_total - grand_done
    eta_secs = None
    if all_walls and rem > 0:
        eta_secs = int(statistics.median(all_walls) * rem)
    recent, fails = recent_cells_and_fails()
    now = time.time()
    status = {
        # ---- original keys (unchanged) ----
        "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "target_n": target, "phase": phase,
        "endpoint_up": endpoint_up(cfg["port"]),
        "container_up": container_running(cfg["container"]),
        "grand_done": grand_done, "grand_total": grand_total,
        "pct": round(100 * grand_done / grand_total, 1) if grand_total else 0,
        "current": cur, "arms": arms, "arms_done": arms_done, "tasks": TASKS,
        # ---- additive enrichments ----
        "eta_secs": eta_secs,                                  # enrichment 3
        "recent_cells": recent,                                # enrichment 3
        "fails": fails,                                        # enrichment 3
        "started_at": started_at,                              # enrichment 3
        "elapsed_secs": int(now - started_at) if isinstance(started_at, (int, float)) else None,
    }
    STATUS.write_text(json.dumps(status, indent=2))
    return status


def run_arm_with_supervision(cfg, arm, target, started_at):
    """Spawn run_microbench for one arm; watchdog endpoint + stuck cells until it exits."""
    label, thinking = arm["label"], arm["thinking"]
    # preclean stale sandboxes + scratch workspaces for this label
    ids = sh("docker ps -aq --filter name=bench-sandbox-").stdout.split()
    if ids:
        sh(["docker", "rm", "-f", *ids])
    sh(f"sudo rm -rf {TOOLING}/workspace/*{label}_v* 2>/dev/null")
    log(f"RUN arm {label} (thinking={thinking}) target N={target}")
    proc = subprocess.Popen(
        ["bash", str(SCRIPTS / "run_microbench.sh"), cfg["model"], str(cfg["port"]),
         label, str(target), "", thinking, str(cfg["max_model_len"])],
        stdout=open(STATE_DIR / f"run-{label}.log", "a"), stderr=subprocess.STDOUT)
    last_endpoint_ok = time.time()
    while proc.poll() is None:
        time.sleep(30)
        write_heartbeat()                                     # enrichment 4
        write_status(cfg, target, f"run:{label}", [], started_at)
        if not endpoint_up(cfg["port"]):
            if time.time() - last_endpoint_ok > 90:
                log("watchdog: endpoint down >90s — restarting")
                ensure_endpoint(cfg)                           # notifies on restart (enrichment 1)
                last_endpoint_ok = time.time()
        else:
            last_endpoint_ok = time.time()
        cur = current_cell_info()
        if cur["cell"] and cur["frozen_secs"] and cur["frozen_secs"] > cfg["stuck_secs"]:
            kill_stuck(cur["cell"])
    log(f"run_microbench {label} exited rc={proc.returncode}")
    # grade + summarize (idempotent)
    sh(f"sudo rm -rf /tmp/grade_*{label}_v* 2>/dev/null")
    g = sh(["bash", str(SCRIPTS / "grade_microbench.sh"), label])
    (STATE_DIR / f"grade-{label}.log").write_text(g.stdout + g.stderr)
    s = sh(["bash", str(SCRIPTS / "summarize.sh"), label])
    (STATE_DIR / f"summary-{label}.txt").write_text(s.stdout + s.stderr)
    log(f"graded+summarized {label}")
    # enrichment 1 + 2: arm-completion notification with median timing
    done, total, pertask, metrics = arm_progress(label, target)
    npass = sum(p["pass"] for p in pertask.values())
    wall = f"{metrics['wall_median']/60:.1f}m" if metrics["wall_median"] else "?"
    tps = f"{metrics['tok_ps_median']}" if metrics["tok_ps_median"] else "?"
    notify("bench: arm complete",
           f"{label} {done}/{total} cells, {npass} pass — median {wall}/cell, {tps} tok/s", 0)


def all_done(cfg, target) -> bool:
    for a in cfg["arms"]:
        done, total, _, _ = arm_progress(a["label"], target)
        if done < total:
            return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target-n", type=int, default=None)
    ap.add_argument("--config", default=None)
    ap.add_argument("--max-passes", type=int, default=6)
    ap.add_argument("--once", action="store_true",
                    help="write a single status snapshot and exit (for external monitors)")  # enrichment 5
    args = ap.parse_args()
    cfg = dict(DEFAULT_CONFIG)
    if args.config and Path(args.config).exists():
        cfg.update(json.loads(Path(args.config).read_text()))

    # enrichment 5: --once snapshot (no target-n required, no driving)
    if args.once:
        prev_n = cfg.get("arms") and DEFAULT_CONFIG.get("port")  # noop, keep structure
        target = args.target_n
        if target is None:
            # best-effort: reuse last target from existing status, else 1
            try:
                target = int(json.loads(STATUS.read_text()).get("target_n", 1))
            except Exception:
                target = 1
        write_status(cfg, target, "snapshot", [])
        print("AUTOPILOT_SNAPSHOT")
        return

    if args.target_n is None:
        ap.error("--target-n is required unless --once is given")
    target = args.target_n

    # enrichment 4: resume-safety — refuse to double-drive
    fh = fresh_heartbeat()
    if fh:
        age, pid = fh
        msg = (f"ABORT: another autopilot heartbeat is fresh ({age:.0f}s old, pid={pid}). "
               f"Refusing to double-drive. If that process is dead, remove {HEARTBEAT}.")
        log(msg)
        print(msg, file=sys.stderr)
        print("AUTOPILOT_ABORTED_DOUBLE_DRIVE")
        sys.exit(3)

    started_at = time.time()
    write_heartbeat()
    log(f"=== AUTOPILOT START target N={target} ===")
    notify("bench: autopilot start", f"N={target}, {len(cfg['arms'])} arms, model {cfg['model']}", 0)  # enrichment 1
    write_status(cfg, target, "starting", [], started_at)
    for p in range(1, args.max_passes + 1):
        if all_done(cfg, target):
            break
        log(f"--- pass {p}/{args.max_passes} ---")
        write_heartbeat()                                     # enrichment 4
        if not ensure_endpoint(cfg):
            log("endpoint unrecoverable; sleeping 60s then retrying"); time.sleep(60); continue
        for a in cfg["arms"]:
            done, total, _, _ = arm_progress(a["label"], target)
            if done < total:
                run_arm_with_supervision(cfg, a, target, started_at)
        write_status(cfg, target, f"pass{p}-done", [a["label"] for a in cfg["arms"]], started_at)
    final = write_status(cfg, target,
                         "COMPLETE" if all_done(cfg, target) else "INCOMPLETE", [], started_at)
    log(f"=== AUTOPILOT DONE phase={final['phase']} {final['grand_done']}/{final['grand_total']} ===")
    # enrichment 1: run-complete notification (high priority on incomplete)
    if final["phase"] == "COMPLETE":
        notify("bench: run COMPLETE",
               f"N={target} done — {final['grand_done']}/{final['grand_total']} cells, "
               f"{len(final['fails'])} fails", 0)
    else:
        notify("bench: run INCOMPLETE",
               f"N={target} stopped at {final['grand_done']}/{final['grand_total']} cells "
               f"after {args.max_passes} passes — {len(final['fails'])} fails", 1)
    print("AUTOPILOT_COMPLETE" if final["phase"] == "COMPLETE" else "AUTOPILOT_INCOMPLETE")


if __name__ == "__main__":
    main()
