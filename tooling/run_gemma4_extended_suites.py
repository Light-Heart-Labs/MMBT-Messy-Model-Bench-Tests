#!/usr/bin/env python3
"""Persistent sharded Gemma 4 runner for the non-microbench MMBT suites."""
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
MATRIX_PATH = TOOLING / "gemma4-31b-q4-extended-matrix.json"
LANE_INDEX = int(os.environ.get("GEMMA_EXTENDED_LANE_INDEX", "0"))
LANE_COUNT = int(os.environ.get("GEMMA_EXTENDED_LANE_COUNT", "1"))
PORT = int(os.environ.get("GEMMA_EXTENDED_PORT", "8000"))
STATE_ROOT = Path("/tmp/mmbt-gemma4-31b-q4-extended")
STATE = STATE_ROOT / f"lane{LANE_INDEX}"
STATUS = STATE / "status.json"
EVENTS = STATE / "events.jsonl"
MAIN_STATUS = Path("/tmp/bench-autopilot/status.json")
MODEL = "Gemma-4-31B-it-QAT-Q4_0"
LAUNCHER = ROOT / "tooling/deployments/gemma4-31b-q4-tower2/ensure-gemma4-winner.sh"
SERVING_MANIFEST = ROOT / "tooling/deployments/gemma4-31b-q4-tower2/benchmark-serving-manifest.json"
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
        write_status(phase="WAITING_FOR_MICROBENCH", lane=LANE_INDEX, port=PORT)
        time.sleep(60)
    event("microbench_gate_passed")


def run_name(suite_id: str, rep: int) -> str:
    names = {
        "dreamserver-1-pr-audit": "n1_gemma4-31b-q4",
        "wallstreet-investment-memo": "gemma4-31b-q4_invest_memo",
        "wallstreet-board-presentation": "gemma4-31b-q4_board_pres",
        "dreamserver-75-pr-audit": "gemma4-31b-q4_75pr",
    }
    return f"{names[suite_id]}_v{rep}"


def terminal_pathology(log_dir: Path) -> bool:
    try:
        label = json.loads((log_dir / "label.json").read_text())
        return label.get("primary") == "identical-call-loop"
    except Exception:
        return False


def terminal_labeled_outcome(log_dir: Path) -> bool:
    """Return whether a run has an explicit terminal benchmark label."""
    try:
        label = json.loads((log_dir / "label.json").read_text())
    except Exception:
        return False
    return bool(label.get("primary"))


def completed(log_dir: Path) -> bool:
    return ((log_dir / "summary.json").exists() and (log_dir / "workspace_final.tar.gz").exists()) \
        or terminal_labeled_outcome(log_dir)


def infra_invalid(log_dir: Path) -> bool:
    """Return whether a completed run is invalid infrastructure evidence.

    MMBT's published failure taxonomy treats both ``api_error: timed out``
    and other ``api_error: ...`` finish reasons as benchmark outcomes.  Do not
    discard or retry those here: they can reflect model context, parser, OOM,
    or single-call latency failures.  The live supervisor separately detects
    an endpoint outage lasting more than 90 seconds and sets
    ``killed_for_infra`` for the genuinely retryable case.
    """
    try:
        reason = str(json.loads((log_dir / "summary.json").read_text()).get("finish_reason") or "")
    except Exception:
        # A missing summary is not evidence of an endpoint outage. It can be
        # a model/tool-schema failure or a harness crash and must not inflate
        # shipped rate through an automatic retry.
        return False
    return reason.startswith("endpoint_")


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


def label_missing_artifacts(log_dir: Path, stdout_path: Path, rc: int) -> str:
    """Record a non-endpoint terminal outcome instead of silently retrying it."""
    log_dir.mkdir(parents=True, exist_ok=True)
    try:
        output = stdout_path.read_text(errors="replace")
    except Exception:
        output = ""
    if "Traceback (most recent call last)" in output:
        primary = "harness-crash"
        sub_labels = ["operator-review-required", "not-auto-scored"]
    else:
        primary = "missing-artifacts"
        sub_labels = ["model-terminal-failure"]
    label = {
        "schema_version": 1,
        "primary": primary,
        "sub_labels": sub_labels,
        "notes": (
            "Harness exited without the required summary/archive and no sustained "
            "endpoint outage was observed. A Python traceback stops the lane for "
            "operator review; otherwise this is a preserved terminal model outcome."
        ),
        "labeler": "extended-suite-supervisor",
        "labeled_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "return_code": rc,
        "harness_output_tail": output[-8000:],
    }
    (log_dir / "label.json").write_text(json.dumps(label, indent=2) + "\n")
    return primary


def harness_command(suite: dict, rep: int, max_model_len: int,
                    top_p: float, top_k: int) -> list[str]:
    name = run_name(suite["id"], rep)
    cmd = [
        "python3", str(TOOLING / "harness.py"), name, str(ROOT / suite["task"]),
        "--model", MODEL, "--port", str(PORT),
        "--temperature", str(suite["temperature"]),
        "--top-p", str(top_p),
        "--top-k", str(top_k),
        "--stuck-threshold", str(suite["stuck_threshold"]),
        "--max-model-len", str(max_model_len),
        "--max-output-tokens-cap", str(suite["max_output_tokens_cap"]),
        "--serving-manifest", str(SERVING_MANIFEST),
        "--docker-socket", "--gpus", "all",
    ]
    if suite.get("require_git_tag"):
        cmd.append("--require-git-tag")
    if suite.get("input_from"):
        source = WORKSPACES / run_name(suite["input_from"], rep)
        cmd += ["--input-mount", str(source)]
    if suite.get("input_path"):
        cmd += ["--input-mount", str(Path(suite["input_path"]).resolve())]
    return cmd


def wait_for_dependency(source_name: str) -> bool:
    """Wait until the corresponding memo ships or gets a terminal label."""
    source_log = LOGS / source_name
    while True:
        if terminal_labeled_outcome(source_log):
            return False
        if completed(source_log):
            return True
        write_status(
            phase="WAITING_FOR_DEPENDENCY", source_run=source_name,
            lane=LANE_INDEX, port=PORT,
        )
        time.sleep(30)


def supervise_one(suite: dict, rep: int, max_model_len: int,
                  top_p: float, top_k: int) -> None:
    name = run_name(suite["id"], rep)
    log_dir = LOGS / name
    if suite.get("input_from"):
        source_name = run_name(suite["input_from"], rep)
        source_log = LOGS / source_name
        if not wait_for_dependency(source_name):
            log_dir.mkdir(parents=True, exist_ok=True)
            source_label = json.loads((source_log / "label.json").read_text())
            label = {
                "schema_version": 1,
                "primary": "dependency-failure",
                "sub_labels": ["input-run-did-not-ship"],
                "notes": (
                    f"Not launched because required input run {source_name} ended "
                    f"with terminal label {source_label.get('primary')}."
                ),
                "labeler": "extended-suite-supervisor",
                "labeled_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "source_run": source_name,
                "source_primary": source_label.get("primary"),
            }
            (log_dir / "label.json").write_text(json.dumps(label, indent=2) + "\n")
            event("run_dependency_failure", run=name, source_run=source_name,
                  source_primary=source_label.get("primary"))
            return
    if completed(log_dir) and not infra_invalid(log_dir):
        event("run_skip_complete", run=name)
        return
    for attempt in range(1, 4):
        if not ensure_endpoint():
            time.sleep(60)
            continue
        if not git_clean():
            raise RuntimeError("extended suite worktree became dirty")
        cmd = harness_command(suite, rep, max_model_len, top_p, top_k)
        stdout_path = STATE / f"{name}-attempt{attempt}.log"
        event("run_start", run=name, suite=suite["id"], rep=rep, attempt=attempt, command=cmd)
        # Publish the run identity before spawning the harness; the telemetry
        # logger independently attributes the live harness PID/port to its GPU.
        write_status(phase="RUNNING", suite=suite["id"], run=name,
                     rep=rep, attempt=attempt, harness_pid=None,
                     lane=LANE_INDEX, port=PORT)
        with stdout_path.open("a") as out:
            proc = subprocess.Popen(cmd, cwd=ROOT, stdout=out, stderr=subprocess.STDOUT)
            write_status(phase="RUNNING", suite=suite["id"], run=name,
                         rep=rep, attempt=attempt, harness_pid=proc.pid,
                         lane=LANE_INDEX, port=PORT)
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
                             rep=rep, attempt=attempt, harness_pid=proc.pid,
                             lane=LANE_INDEX, port=PORT)
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
        primary = label_missing_artifacts(log_dir, stdout_path, rc)
        event("run_terminal_failure", run=name, attempt=attempt, rc=rc,
              primary=primary)
        if primary == "harness-crash":
            raise RuntimeError(f"{name} hit a harness traceback; operator review required")
        return
    raise RuntimeError(f"{name} exhausted three infrastructure retries")


def validate_matrix(matrix: dict) -> None:
    if LANE_COUNT < 1 or not 0 <= LANE_INDEX < LANE_COUNT:
        raise RuntimeError(f"invalid lane {LANE_INDEX}/{LANE_COUNT}")
    lane_ports = [int(port) for port in matrix.get("lane_ports", [8000])]
    if len(lane_ports) != LANE_COUNT or lane_ports[LANE_INDEX] != PORT:
        raise RuntimeError(
            f"lane wiring mismatch: lane={LANE_INDEX}/{LANE_COUNT} port={PORT} "
            f"matrix_ports={lane_ports}"
        )
    if not SERVING_MANIFEST.is_file():
        raise RuntimeError(f"serving manifest missing: {SERVING_MANIFEST}")
    protocol = ROOT / matrix["substantive_audit_protocol"]
    if not protocol.is_file():
        raise RuntimeError(f"substantive audit protocol missing: {protocol}")
    protocol_hash = sha256(protocol)
    if protocol_hash != matrix["substantive_audit_protocol_sha256"]:
        raise RuntimeError(f"substantive audit protocol hash mismatch: {protocol_hash}")
    for suite in matrix["suites"]:
        task = ROOT / suite["task"]
        actual = sha256(task)
        if actual != suite["current_task_sha256"]:
            raise RuntimeError(f"task hash mismatch for {suite['id']}: {actual}")
        if suite.get("subject_pin"):
            subject_pin = ROOT / suite["subject_pin"]
            if not subject_pin.is_file():
                raise RuntimeError(f"subject pin missing for {suite['id']}: {subject_pin}")
            actual_pin = sha256(subject_pin)
            if actual_pin != suite.get("subject_pin_sha256"):
                raise RuntimeError(
                    f"subject pin hash mismatch for {suite['id']}: {actual_pin}"
                )
        if suite.get("input_from") and suite.get("input_path"):
            raise RuntimeError(f"suite {suite['id']} cannot set both input_from and input_path")
        if suite.get("input_path") and not Path(suite["input_path"]).is_dir():
            raise RuntimeError(
                f"input fixture missing for {suite['id']}: {suite['input_path']}"
            )


def main() -> None:
    matrix = json.loads(MATRIX_PATH.read_text())
    validate_matrix(matrix)
    max_model_len = int(matrix["served_context_tokens"])
    if max_model_len <= 0:
        raise RuntimeError("served_context_tokens must be positive")
    top_p = float(matrix["top_p"])
    if not 0.0 < top_p <= 1.0:
        raise RuntimeError("top_p must be in (0, 1]")
    top_k = int(matrix["top_k"])
    if top_k <= 0:
        raise RuntimeError("top_k must be positive")
    if "--validate-only" in sys.argv[1:]:
        print(
            f"VALID: {len(matrix['suites'])} suites x N={matrix['replicates']} "
            f"lane={LANE_INDEX}/{LANE_COUNT} port={PORT}"
        )
        return
    wait_for_microbench()
    if not git_clean():
        raise SystemExit("refusing extended suites from dirty worktree")
    all_jobs = [
        (suite, rep)
        for suite in matrix["suites"]
        for rep in range(1, matrix["replicates"] + 1)
    ]
    jobs = [job for ordinal, job in enumerate(all_jobs) if ordinal % LANE_COUNT == LANE_INDEX]
    total = len(jobs)
    done = 0
    for suite, rep in jobs:
        supervise_one(suite, rep, max_model_len, top_p, top_k)
        done += 1
        write_status(phase="RUNNING", done=done, total=total,
                     suite=suite["id"], rep=rep, lane=LANE_INDEX, port=PORT)
    write_status(phase="COMPLETE", done=done, total=total,
                 lane=LANE_INDEX, port=PORT)
    event("extended_lane_complete", done=done, total=total,
          lane=LANE_INDEX, port=PORT)


if __name__ == "__main__":
    main()
