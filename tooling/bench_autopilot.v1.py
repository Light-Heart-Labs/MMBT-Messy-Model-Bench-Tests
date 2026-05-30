#!/usr/bin/env python3
"""bench_autopilot — self-healing supervisor for the MMBT microbench.

Replaces hand-babysitting a long run: launches/keeps the llama.cpp endpoint alive,
runs both reasoning arms to a target N (idempotent), kills genuinely-stuck cells,
grades + summarizes, and continuously emits a status.json the dashboard renders.

Usage:
  python3 bench_autopilot.py --target-n 20 [--config bench_autopilot.config.json]

Design: run_microbench/grade/summarize are idempotent, so the supervisor just loops
them until every target cell exists, restarting the endpoint and clearing stuck
cells between/within passes. Safe to kill and re-launch at any time.
"""
from __future__ import annotations
import argparse, json, os, signal, subprocess, sys, time
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
            return False
        time.sleep(5)
    log("ERROR: endpoint did not come up within grace period")
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


def arm_progress(label: str, target: int):
    """Return (done, total, per_task_counts) for an arm up to target N."""
    total = len(TASKS) * target
    done = 0
    pertask = {}
    for t in TASKS:
        c = 0
        passes = 0
        for v in range(1, target + 1):
            rn = f"{t}_{label}_v{v}"
            if cell_done(rn):
                c += 1; done += 1
                if cell_verdict(rn) in ("PASS", "STRUCTURAL_PASS"):
                    passes += 1
        pertask[t] = {"done": c, "pass": passes}
    return done, total, pertask


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


def write_status(cfg, target, phase, arms_done):
    arms = []
    grand_done = grand_total = 0
    for a in cfg["arms"]:
        done, total, pertask = arm_progress(a["label"], target)
        grand_done += done; grand_total += total
        arms.append({"label": a["label"], "done": done, "total": total, "pertask": pertask})
    cur = current_cell_info()
    status = {
        "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "target_n": target, "phase": phase,
        "endpoint_up": endpoint_up(cfg["port"]),
        "container_up": container_running(cfg["container"]),
        "grand_done": grand_done, "grand_total": grand_total,
        "pct": round(100 * grand_done / grand_total, 1) if grand_total else 0,
        "current": cur, "arms": arms, "arms_done": arms_done, "tasks": TASKS,
    }
    STATUS.write_text(json.dumps(status, indent=2))
    return status


def run_arm_with_supervision(cfg, arm, target):
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
        write_status(cfg, target, f"run:{label}", [])
        if not endpoint_up(cfg["port"]):
            if time.time() - last_endpoint_ok > 90:
                log("watchdog: endpoint down >90s — restarting")
                ensure_endpoint(cfg)
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


def all_done(cfg, target) -> bool:
    for a in cfg["arms"]:
        done, total, _ = arm_progress(a["label"], target)
        if done < total:
            return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target-n", type=int, required=True)
    ap.add_argument("--config", default=None)
    ap.add_argument("--max-passes", type=int, default=6)
    args = ap.parse_args()
    cfg = dict(DEFAULT_CONFIG)
    if args.config and Path(args.config).exists():
        cfg.update(json.loads(Path(args.config).read_text()))
    target = args.target_n
    log(f"=== AUTOPILOT START target N={target} ===")
    write_status(cfg, target, "starting", [])
    for p in range(1, args.max_passes + 1):
        if all_done(cfg, target):
            break
        log(f"--- pass {p}/{args.max_passes} ---")
        if not ensure_endpoint(cfg):
            log("endpoint unrecoverable; sleeping 60s then retrying"); time.sleep(60); continue
        for a in cfg["arms"]:
            done, total, _ = arm_progress(a["label"], target)
            if done < total:
                run_arm_with_supervision(cfg, a, target)
        write_status(cfg, target, f"pass{p}-done", [a["label"] for a in cfg["arms"]])
    final = write_status(cfg, target, "COMPLETE" if all_done(cfg, target) else "INCOMPLETE", [])
    log(f"=== AUTOPILOT DONE phase={final['phase']} {final['grand_done']}/{final['grand_total']} ===")
    print("AUTOPILOT_COMPLETE" if final["phase"] == "COMPLETE" else "AUTOPILOT_INCOMPLETE")


if __name__ == "__main__":
    main()
