#!/usr/bin/env python3
"""Persistent DeepSeek V4 Flash runner for the non-microbench MMBT suites."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLING = ROOT / "tooling"
LOGS = ROOT / "logs"
WORKSPACES = TOOLING / "workspace"
MATRIX_PATH = TOOLING / "deepseek-v4-flash-extended-matrix.json"
STATE = Path("/tmp/mmbt-deepseek-v4-flash-extended")
STATUS = STATE / "status.json"
EVENTS = STATE / "events.jsonl"
MAIN_STATUS = Path("/tmp/bench-autopilot/status.json")
MAIN_SERVICE = "mmbt-deepseek-v4-flash-0731-clean2.service"
MODEL = "DeepSeek-V4-Flash-0731"
PORT = 8000
LAUNCHER = Path("/home/michael/start-deepseek-v4-flash-0731.sh")
SUBSTANCE = TOOLING / "scripts" / "check_substance.py"
STATE.mkdir(parents=True, exist_ok=True)


def event(kind: str, **data) -> None:
    row = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "kind": kind, **data}
    with EVENTS.open("a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")
    print(json.dumps(row, sort_keys=True), flush=True)


def write_status(**data) -> None:
    data["updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    tmp = STATUS.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    tmp.replace(STATUS)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def endpoint_up() -> bool:
    return subprocess.run(
        ["curl", "-fsS", "--max-time", "5", f"http://127.0.0.1:{PORT}/v1/models"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def ensure_endpoint() -> bool:
    if endpoint_up():
        return True
    event("endpoint_restart", launcher=str(LAUNCHER))
    subprocess.run(["bash", str(LAUNCHER)], check=False)
    for _ in range(60):
        if endpoint_up():
            event("endpoint_recovered")
            return True
        time.sleep(5)
    event("endpoint_recovery_failed")
    return False


def git_clean() -> bool:
    r = subprocess.run(
        ["git", "-C", str(ROOT), "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    if r.stdout.strip():
        event("dirty_worktree", details=r.stdout.strip())
        return False
    return True


def main_microbench_complete() -> bool:
    try:
        j = json.loads(MAIN_STATUS.read_text())
    except Exception:
        return False
    return j.get("phase") == "COMPLETE" and j.get("grand_done") == j.get("grand_total") == 120


def wait_for_microbench() -> None:
    while not main_microbench_complete():
        active = subprocess.run(
            ["systemctl", "--user", "is-active", MAIN_SERVICE],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
        write_status(phase="WAITING_FOR_MICROBENCH", main_service=active)
        time.sleep(60)
    event("microbench_gate_passed")


def run_name(suite_id: str, rep: int) -> str:
    names = {
        "dreamserver-1-pr-audit": "n1_deepseek-v4-flash-0731",
        "wallstreet-investment-memo": "deepseek-v4-flash-0731_invest_memo",
        "wallstreet-board-presentation": "deepseek-v4-flash-0731_board_pres",
        "dreamserver-75-pr-audit": "deepseek-v4-flash-0731_75pr",
    }
    return f"{names[suite_id]}_v{rep}"


def terminal_pathology(log_dir: Path) -> bool:
    try:
        label = json.loads((log_dir / "label.json").read_text())
        return label.get("primary") == "identical-call-loop"
    except Exception:
        return False


def completed(log_dir: Path) -> bool:
    return ((log_dir / "summary.json").exists() and (log_dir / "workspace_final.tar.gz").exists()) \
        or terminal_pathology(log_dir)


def infra_invalid(log_dir: Path) -> bool:
    try:
        reason = str(json.loads((log_dir / "summary.json").read_text()).get("finish_reason") or "")
    except Exception:
        return not terminal_pathology(log_dir)
    return reason.startswith("api_error") or reason.startswith("endpoint_")


def archive_invalid(name: str, attempt: int) -> None:
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    invalid_root = LOGS / "_infra_invalid"
    invalid_root.mkdir(parents=True, exist_ok=True)
    src = LOGS / name
    if src.exists():
        shutil.move(str(src), str(invalid_root / f"{name}-attempt{attempt}-{stamp}"))
    ws = WORKSPACES / name
    if ws.exists():
        ws_invalid = WORKSPACES / "_infra_invalid"
        ws_invalid.mkdir(parents=True, exist_ok=True)
        shutil.move(str(ws), str(ws_invalid / f"{name}-attempt{attempt}-{stamp}"))


def label_scroll_loop(log_dir: Path, check_output: str) -> None:
    label = {
        "primary": "identical-call-loop",
        "sub_labels": ["scroll-loop"],
        "notes": "Exact-PID SIGTERM after the published >=30 identical digit-stripped command rule.",
        "labeler": "extended-suite-supervisor",
        "labeled_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "substance_check": check_output[-4000:],
    }
    (log_dir / "label.json").write_text(json.dumps(label, indent=2) + "\n")


def harness_command(suite: dict, rep: int) -> list[str]:
    name = run_name(suite["id"], rep)
    cmd = [
        "python3", str(TOOLING / "harness.py"), name, str(ROOT / suite["task"]),
        "--model", MODEL, "--port", str(PORT),
        "--temperature", str(suite["temperature"]),
        "--stuck-threshold", str(suite["stuck_threshold"]),
        "--max-model-len", "131072",
        "--max-output-tokens-cap", str(suite["max_output_tokens_cap"]),
        "--docker-socket", "--gpus", "all",
    ]
    if suite.get("require_git_tag"):
        cmd.append("--require-git-tag")
    if suite.get("input_from"):
        source = WORKSPACES / run_name(suite["input_from"], rep)
        cmd += ["--input-mount", str(source)]
    return cmd


def supervise_one(suite: dict, rep: int) -> None:
    name = run_name(suite["id"], rep)
    log_dir = LOGS / name
    if completed(log_dir) and not infra_invalid(log_dir):
        event("run_skip_complete", run=name)
        return
    for attempt in range(1, 4):
        if not ensure_endpoint():
            time.sleep(60)
            continue
        if not git_clean():
            raise RuntimeError("extended suite worktree became dirty")
        cmd = harness_command(suite, rep)
        stdout_path = STATE / f"{name}-attempt{attempt}.log"
        event("run_start", run=name, suite=suite["id"], rep=rep, attempt=attempt, command=cmd)
        with stdout_path.open("a") as out:
            proc = subprocess.Popen(cmd, cwd=ROOT, stdout=out, stderr=subprocess.STDOUT)
            last_substance = 0.0
            endpoint_down_since = None
            killed_for_infra = False
            while proc.poll() is None:
                time.sleep(30)
                transcript = log_dir / "transcript.jsonl"
                now = time.time()
                if transcript.exists() and now - last_substance >= 300:
                    last_substance = now
                    check = subprocess.run(
                        ["python3", str(SUBSTANCE), str(transcript)],
                        capture_output=True, text=True, check=False,
                    )
                    event("substance", run=name, rc=check.returncode)
                    if check.returncode == 1:
                        proc.terminate()
                        try:
                            proc.wait(timeout=20)
                        except subprocess.TimeoutExpired:
                            proc.kill()
                        label_scroll_loop(log_dir, (check.stdout or "") + (check.stderr or ""))
                        subprocess.run(["docker", "rm", "-f", f"bench-sandbox-{name}"],
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        event("run_terminal_pathology", run=name, pathology="scroll-loop")
                        return
                if endpoint_up():
                    endpoint_down_since = None
                elif endpoint_down_since is None:
                    endpoint_down_since = now
                elif now - endpoint_down_since > 90:
                    proc.terminate()
                    try:
                        proc.wait(timeout=20)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                    killed_for_infra = True
                    event("run_killed_for_endpoint", run=name)
                    break
                write_status(phase="RUNNING", suite=suite["id"], run=name,
                             rep=rep, attempt=attempt, harness_pid=proc.pid)
            rc = proc.wait()
        if killed_for_infra or infra_invalid(log_dir):
            event("run_infra_invalid", run=name, attempt=attempt, rc=rc)
            archive_invalid(name, attempt)
            ensure_endpoint()
            continue
        if completed(log_dir):
            subprocess.run(
                ["python3", str(TOOLING / "scripts" / "extract_cost.py"), str(log_dir)],
                cwd=ROOT, check=False,
            )
            event("run_complete", run=name, attempt=attempt, rc=rc)
            return
        event("run_missing_artifacts", run=name, attempt=attempt, rc=rc)
        archive_invalid(name, attempt)
    raise RuntimeError(f"{name} exhausted three infrastructure retries")


def validate_matrix(matrix: dict) -> None:
    for suite in matrix["suites"]:
        task = ROOT / suite["task"]
        actual = sha256(task)
        if actual != suite["current_task_sha256"]:
            raise RuntimeError(f"task hash mismatch for {suite['id']}: {actual}")


def main() -> None:
    matrix = json.loads(MATRIX_PATH.read_text())
    validate_matrix(matrix)
    if "--validate-only" in sys.argv[1:]:
        print(f"VALID: {len(matrix['suites'])} suites x N={matrix['replicates']}")
        return
    wait_for_microbench()
    if not git_clean():
        raise SystemExit("refusing extended suites from dirty worktree")
    total = len(matrix["suites"]) * matrix["replicates"]
    done = 0
    for suite in matrix["suites"]:
        for rep in range(1, matrix["replicates"] + 1):
            supervise_one(suite, rep)
            done += 1
            write_status(phase="RUNNING", done=done, total=total,
                         suite=suite["id"], rep=rep)
    write_status(phase="COMPLETE", done=done, total=total)
    event("extended_matrix_complete", done=done, total=total)


if __name__ == "__main__":
    main()
