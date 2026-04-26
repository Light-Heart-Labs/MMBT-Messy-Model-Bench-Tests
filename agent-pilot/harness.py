#!/usr/bin/env python3
"""Minimal agent harness: vLLM tool-calling loop + Docker sandbox execution.

Usage: harness.py <run_name> <task_file> [--max-iters N] [--model NAME] [--port P]
"""
import argparse, json, os, subprocess, sys, time, hashlib, uuid
from datetime import datetime, timezone
from pathlib import Path
import urllib.request, urllib.error

SANDBOX = "bench-sandbox-run"  # default; overridden per-run in main() so parallel runs can coexist
IMAGE = "bench-sandbox:latest"


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def docker_inspect(name, fmt=None):
    cmd = ["docker", "inspect", name]
    if fmt:
        cmd = ["docker", "inspect", "--format", fmt, name]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else None


def record_environment(run_name, model, api_url, task_file, log_dir):
    """Capture everything needed to reproduce the run. Written before the loop starts."""
    receipt = {
        "schema_version": 1,
        "run_name": run_name,
        "captured_at": now_iso(),
        "host": {
            "hostname": subprocess.run(["hostname"], capture_output=True, text=True).stdout.strip(),
            "kernel": subprocess.run(["uname", "-r"], capture_output=True, text=True).stdout.strip(),
            "os": subprocess.run(["lsb_release", "-d"], capture_output=True, text=True).stdout.strip() or "unknown",
        },
        "harness": {
            "path": str(Path(__file__).resolve()),
            "git_sha": subprocess.run(
                ["git", "-C", str(Path(__file__).resolve().parent.parent), "rev-parse", "HEAD"],
                capture_output=True, text=True,
            ).stdout.strip() or None,
            "git_dirty": bool(subprocess.run(
                ["git", "-C", str(Path(__file__).resolve().parent.parent), "status", "--porcelain"],
                capture_output=True, text=True,
            ).stdout.strip()),
            "file_sha256": file_sha256(__file__),
        },
        "task": {
            "path": str(Path(task_file).resolve()),
            "sha256": file_sha256(task_file),
            "byte_size": os.path.getsize(task_file),
        },
        "vllm": {
            "served_model_name": model,
            "api_url": api_url,
        },
        "sandbox": {
            "image": IMAGE,
        },
    }

    # Try to identify the vLLM container serving this model by hitting the URL's port
    # Best-effort: list vllm-* containers and capture inspect for each
    p = subprocess.run(
        ["docker", "ps", "--filter", "name=vllm-", "--format", "{{.Names}}"],
        capture_output=True, text=True,
    )
    receipt["vllm"]["containers"] = []
    for cname in p.stdout.split():
        info = docker_inspect(cname, fmt='{{.Image}}|{{.Id}}|{{.State.StartedAt}}|{{json .Args}}|{{json .Config.Cmd}}|{{json .HostConfig.PortBindings}}')
        if not info: continue
        parts = info.split("|", 5)
        image_ref, cid, started_at, args_json, cmd_json, ports_json = (parts + [None]*6)[:6]
        # Resolve image digest
        image_digest = docker_inspect(image_ref, fmt='{{index .RepoDigests 0}}') or "unknown"
        receipt["vllm"]["containers"].append({
            "name": cname,
            "image_ref": image_ref,
            "image_digest": image_digest,
            "container_id": cid,
            "started_at": started_at,
            "args": json.loads(args_json) if args_json else [],
            "cmd": json.loads(cmd_json) if cmd_json else [],
            "port_bindings": json.loads(ports_json) if ports_json else {},
        })

    # Sandbox image digest
    sandbox_img_id = docker_inspect(IMAGE, fmt='{{.Id}}')
    receipt["sandbox"]["image_id"] = sandbox_img_id

    # nvidia-smi snapshot
    nvs = subprocess.run(
        ["nvidia-smi", "--query-gpu=index,name,driver_version,power.limit,power.draw,temperature.gpu,memory.used,memory.total,clocks.current.graphics",
         "--format=csv,noheader"],
        capture_output=True, text=True,
    )
    receipt["hardware"] = {"nvidia_smi": nvs.stdout.strip().splitlines()}

    # Inference request defaults (the constants used in the loop body)
    receipt["inference_request_defaults"] = {
        "temperature": 0.0,
        "max_tokens_strategy": "min(64000, max_model_len - last_prompt_tokens - 14000)",
        "max_model_len": 262144,
        "stream": False,
        "tool_choice": "auto",
        "tools": [t["function"]["name"] for t in TOOLS],
    }

    receipt["harness_loop_config"] = {
        "stuck_threshold_iters": 30,
        "max_iters_default": 10000,
        "max_completion_total_default": 10**12,
    }

    out = Path(log_dir) / "receipt.json"
    out.write_text(json.dumps(receipt, indent=2))
    return receipt


def workspace_state_hash():
    """Hash of workspace file contents (skipping .git/objects for speed).
    Detects: file writes, file mods, file deletes, new commits (refs change)."""
    cmd = (
        "find /workspace -path '*/.git/objects' -prune -o -type f -print 2>/dev/null "
        "| sort | xargs -r sha1sum 2>/dev/null | sha1sum | awk '{print $1}'"
    )
    p = subprocess.run(["docker", "exec", SANDBOX, "bash", "-c", cmd],
                       capture_output=True, text=True, timeout=30)
    return p.stdout.strip()


def docker_exec(cmd, workdir="/workspace", timeout=300):
    """Run a command in the sandbox. Returns dict with stdout/stderr/rc/duration.

    Pipes the command via stdin (`bash -s`) instead of `bash -c "..."` so we
    don't hit Linux's ~128KB argv limit on long heredocs. Hit this when a
    model emitted a 680-token python heredoc as a single bash call.
    """
    t0 = time.time()
    full = ["docker", "exec", "-i", "-w", workdir, SANDBOX, "bash", "-s"]
    try:
        p = subprocess.run(full, input=cmd, capture_output=True, text=True, timeout=timeout)
        return {
            "rc": p.returncode,
            "stdout": p.stdout[-20000:],
            "stderr": p.stderr[-5000:],
            "duration_s": round(time.time() - t0, 2),
            "truncated_stdout": len(p.stdout) > 20000,
        }
    except subprocess.TimeoutExpired:
        return {"rc": -1, "stdout": "", "stderr": f"timeout after {timeout}s", "duration_s": timeout}


# ----- Tools available to the agent --------------------------------------

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Run a bash command inside the sandbox container. Use this for shell, git, curl, python, file ops — anything you'd do at a terminal. CWD is /workspace by default. Output is truncated to last 20KB.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Bash command to execute."},
                    "workdir": {"type": "string", "description": "Working directory. Default /workspace.", "default": "/workspace"},
                    "timeout_s": {"type": "integer", "description": "Timeout in seconds. Default 300.", "default": 300},
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write text content to a file at the given path inside the sandbox. Creates parent directories. Overwrites if exists. Use for any file > a few lines, or anything where heredoc escaping in bash would be painful.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute or relative path (relative to /workspace)."},
                    "content": {"type": "string", "description": "File content."},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file from the sandbox. Returns up to 200KB.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "done",
            "description": "Signal that the task is complete. Provide a short summary of what was accomplished.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                },
                "required": ["summary"],
            },
        },
    },
]


def execute_tool(name, args, log_dir):
    if name == "bash":
        cmd = args.get("command", "")
        workdir = args.get("workdir") or "/workspace"
        timeout = int(args.get("timeout_s") or 300)
        r = docker_exec(cmd, workdir=workdir, timeout=timeout)
        body = f"rc={r['rc']}  duration={r['duration_s']}s\n--- stdout ---\n{r['stdout']}"
        if r['stderr']:
            body += f"\n--- stderr ---\n{r['stderr']}"
        if r.get('truncated_stdout'):
            body += "\n[stdout truncated]"
        return body
    elif name == "write_file":
        path = args["path"]
        if not path.startswith("/"):
            path = "/workspace/" + path
        content = args["content"]
        # Stage via tempfile on host, docker cp into sandbox (handles binary/special chars cleanly)
        tmp = Path(log_dir) / f".write_{uuid.uuid4().hex}.tmp"
        tmp.write_text(content, encoding="utf-8")
        # Ensure parent dir exists in sandbox
        parent = os.path.dirname(path) or "/workspace"
        docker_exec(f"mkdir -p {parent!r}", timeout=10)
        cp = subprocess.run(["docker", "cp", str(tmp), f"{SANDBOX}:{path}"], capture_output=True, text=True)
        tmp.unlink(missing_ok=True)
        if cp.returncode != 0:
            return f"ERROR copying file: {cp.stderr}"
        size = len(content.encode())
        return f"wrote {size} bytes to {path}"
    elif name == "read_file":
        path = args["path"]
        if not path.startswith("/"):
            path = "/workspace/" + path
        r = docker_exec(f"head -c 200000 {path!r}", timeout=10)
        if r["rc"] != 0:
            return f"ERROR: {r['stderr']}"
        return r["stdout"]
    elif name == "done":
        return "DONE_SIGNAL:" + (args.get("summary") or "")
    else:
        return f"unknown tool {name!r}"


# ----- Agent loop --------------------------------------------------------

def agent_loop(api_url, model, system_prompt, task, log_dir, max_iters=10000,
               max_completion_total=10**12, max_model_len=262144,
               stuck_threshold=30):
    """Run the agent until done() or limits hit. Returns final state dict."""
    log_path = Path(log_dir) / "transcript.jsonl"
    summary_path = Path(log_dir) / "summary.json"

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": task})

    iter_count = 0
    total_completion_tokens = 0
    total_prompt_tokens = 0
    started = time.time()
    done_summary = None
    finish_reason = None
    last_prompt_tokens = 0
    last_workspace_hash = workspace_state_hash()
    iters_since_progress = 0

    while iter_count < max_iters:
        iter_count += 1
        # Dynamic max_tokens: leave room for the next prompt to actually fit.
        # Estimate growth: prior prompt + ~12K for the new tool result/system overhead.
        estimated_prompt = max(last_prompt_tokens + 12000, 8000)
        safety = 2048
        max_tokens_safe = max(2048, max_model_len - estimated_prompt - safety)
        max_tokens_safe = min(max_tokens_safe, 180000)
        body = json.dumps({
            "model": model,
            "messages": messages,
            "tools": TOOLS,
            "tool_choice": "auto",
            "temperature": 0.0,
            "max_tokens": max_tokens_safe,
            "stream": False,
        }).encode()
        req = urllib.request.Request(api_url, data=body, headers={"Content-Type": "application/json"})
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=3600) as r:
                resp = json.loads(r.read())
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            err_body = ""
            if isinstance(e, urllib.error.HTTPError):
                try: err_body = e.read().decode()[:500]
                except: pass
            with open(log_path, "a") as f:
                f.write(json.dumps({"t": now_iso(), "iter": iter_count, "type": "error", "error": str(e), "body": err_body}) + "\n")
            finish_reason = f"api_error: {e}"
            break
        wall = time.time() - t0
        msg = resp["choices"][0]["message"]
        usage = resp.get("usage", {})
        total_completion_tokens += usage.get("completion_tokens", 0)
        total_prompt_tokens += usage.get("prompt_tokens", 0)
        last_prompt_tokens = usage.get("prompt_tokens", last_prompt_tokens)

        # Log the model turn
        with open(log_path, "a") as f:
            f.write(json.dumps({
                "t": now_iso(), "iter": iter_count, "type": "model",
                "wall_s": round(wall, 2),
                "completion_tokens": usage.get("completion_tokens", 0),
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "tok_ps": round(usage.get("completion_tokens", 0) / max(wall, 0.01), 1),
                "content_len": len(msg.get("content") or ""),
                "tool_calls": [{"name": tc["function"]["name"], "args_len": len(tc["function"]["arguments"])} for tc in (msg.get("tool_calls") or [])],
                "finish_reason": resp["choices"][0].get("finish_reason"),
            }) + "\n")

        # If the model hit max_tokens mid-output, its tool_calls JSON arguments may be truncated.
        # Forwarding a malformed assistant message will get rejected by vLLM on the next call.
        # Break cleanly with a clear finish_reason instead.
        if resp["choices"][0].get("finish_reason") == "length":
            with open(log_path, "a") as f:
                f.write(json.dumps({
                    "t": now_iso(), "iter": iter_count, "type": "abort",
                    "reason": "model hit max_tokens cap mid-emission; assistant message likely contains truncated tool-call JSON",
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "max_tokens_safe": max_tokens_safe,
                }) + "\n")
            finish_reason = f"model_exceeded_max_tokens_{max_tokens_safe}"
            break

        # Append assistant message to history (preserve tool_calls so the model sees its own tool intents)
        assistant_msg = {"role": "assistant", "content": msg.get("content") or ""}
        if msg.get("tool_calls"):
            assistant_msg["tool_calls"] = msg["tool_calls"]
        messages.append(assistant_msg)

        tool_calls = msg.get("tool_calls") or []
        if not tool_calls:
            # No tool call — model has finished or is just talking
            content = msg.get("content") or ""
            print(f"[iter {iter_count}] no tool call, content_len={len(content)}, finish={resp['choices'][0].get('finish_reason')}")
            if resp["choices"][0].get("finish_reason") == "stop":
                # Model believes it's done. Treat as soft-done.
                done_summary = content[:1000] if content else "(model stopped without explicit done())"
                finish_reason = "model_stopped"
                break
            # If finish_reason is "length" or other, stop too
            finish_reason = resp["choices"][0].get("finish_reason") or "no_action"
            break

        # Execute each tool call, append result
        soft_done = False
        for tc in tool_calls:
            tc_name = tc["function"]["name"]
            try:
                tc_args = json.loads(tc["function"]["arguments"])
            except json.JSONDecodeError as e:
                tc_args = {}
                result = f"ERROR parsing tool args: {e}\nraw: {tc['function']['arguments'][:500]}"
            else:
                t1 = time.time()
                result = execute_tool(tc_name, tc_args, log_dir)
                tool_wall = time.time() - t1
                with open(log_path, "a") as f:
                    f.write(json.dumps({
                        "t": now_iso(), "iter": iter_count, "type": "tool",
                        "name": tc_name, "args": tc_args if len(json.dumps(tc_args)) < 50000 else {"_truncated_at_bytes": len(json.dumps(tc_args))},
                        "wall_s": round(tool_wall, 2),
                        "result_len": len(result),
                    }) + "\n")
                if result.startswith("DONE_SIGNAL:"):
                    done_summary = result[len("DONE_SIGNAL:"):]
                    soft_done = True

            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": result if not result.startswith("DONE_SIGNAL:") else "task marked done",
            })

        # Stuck detector: workspace state hash unchanged for N iters → kill
        cur_hash = workspace_state_hash()
        if cur_hash == last_workspace_hash:
            iters_since_progress += 1
        else:
            iters_since_progress = 0
            last_workspace_hash = cur_hash

        print(f"[iter {iter_count}] {len(tool_calls)} tool call(s)  wall={wall:.1f}s  ctok={usage.get('completion_tokens',0)}  ptok={last_prompt_tokens}  total_ctok={total_completion_tokens}  no-progress={iters_since_progress}/{stuck_threshold}  max_tok_req={max_tokens_safe}")

        if soft_done:
            finish_reason = "done_signal"
            break
        if total_completion_tokens >= max_completion_total:
            finish_reason = "completion_token_cap"
            break
        if iters_since_progress >= stuck_threshold:
            finish_reason = f"stuck_no_workspace_change_for_{stuck_threshold}_iters"
            break

    elapsed = time.time() - started
    summary = {
        "started_at": datetime.fromtimestamp(started, tz=timezone.utc).isoformat(),
        "ended_at": now_iso(),
        "elapsed_s": round(elapsed, 1),
        "iterations": iter_count,
        "total_completion_tokens": total_completion_tokens,
        "total_prompt_tokens": total_prompt_tokens,
        "model": model,
        "finish_reason": finish_reason,
        "done_summary": done_summary,
    }
    summary_path.write_text(json.dumps(summary, indent=2))
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_name")
    ap.add_argument("task_file")
    ap.add_argument("--max-iters", type=int, default=10000)
    ap.add_argument("--model", default="qwen3-coder-next-awq")
    ap.add_argument("--port", type=int, default=8001)
    ap.add_argument("--system", default=None, help="Path to system prompt file (optional).")
    args = ap.parse_args()

    # Per-run sandbox name so multiple harness invocations don't collide on the same container.
    global SANDBOX
    SANDBOX = f"bench-sandbox-{args.run_name}"

    log_dir = Path("/home/michael/bench/agent-pilot/logs") / args.run_name
    log_dir.mkdir(parents=True, exist_ok=True)
    workspace_host = Path("/home/michael/bench/agent-pilot/workspace") / args.run_name
    if workspace_host.exists():
        subprocess.run(["rm", "-rf", str(workspace_host)], check=True)
    workspace_host.mkdir(parents=True, exist_ok=True)

    # Stop any prior sandbox, start a fresh one with the workspace mounted
    subprocess.run(["docker", "rm", "-f", SANDBOX], capture_output=True)
    subprocess.run([
        "docker", "run", "-d", "--name", SANDBOX,
        "-v", f"{workspace_host}:/workspace",
        "--network", "bridge",
        IMAGE
    ], check=True, capture_output=True)
    # Init git inside the sandbox
    docker_exec("git init -q && git commit --allow-empty -m 'initial empty repo' -q || true", timeout=20)

    task = Path(args.task_file).read_text()
    system_prompt = Path(args.system).read_text() if args.system else None

    api_url = f"http://127.0.0.1:{args.port}/v1/chat/completions"
    print(f"=== Run {args.run_name} | model={args.model} | url={api_url} ===")
    print(f"workspace: {workspace_host}")
    print(f"logs: {log_dir}")

    receipt = record_environment(args.run_name, args.model, api_url, args.task_file, log_dir)
    print(f"receipt -> {log_dir / 'receipt.json'}  (vllm containers logged: {len(receipt['vllm']['containers'])})")

    summary = agent_loop(api_url, args.model, system_prompt, task, log_dir, max_iters=args.max_iters)
    print("\n=== SUMMARY ===")
    print(json.dumps(summary, indent=2))

    # Snapshot the final workspace as a tarball for archival
    tarball = log_dir / "workspace_final.tar.gz"
    subprocess.run(["tar", "czf", str(tarball), "-C", str(workspace_host), "."], check=True)
    print(f"\nworkspace archived -> {tarball}")


if __name__ == "__main__":
    main()
