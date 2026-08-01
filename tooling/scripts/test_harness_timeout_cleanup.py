#!/usr/bin/env python3
"""Regression test: a timed-out tool call must not leave nested descendants."""

import importlib.util
import json
import subprocess
import uuid
from pathlib import Path


HARNESS_PATH = Path(__file__).resolve().parents[1] / "harness.py"


def load_harness():
    spec = importlib.util.spec_from_file_location("mmbt_harness", HARNESS_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main():
    harness = load_harness()
    container = f"mmbt-timeout-cleanup-test-{uuid.uuid4().hex[:12]}"
    try:
        subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--init",
                "--name",
                container,
                harness.IMAGE,
                "sleep",
                "infinity",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        harness.SANDBOX = container

        normal = harness.docker_exec(
            "printf 'hello\\n'; printf 'warn\\n' >&2",
            timeout=2,
        )
        timed = harness.docker_exec(
            "timeout 60 python3 -c 'import time; time.sleep(60)'",
            timeout=2,
        )
        top = subprocess.run(
            ["docker", "top", container, "-eo", "pid,ppid,pgid,sid,stat,args"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout

        assert normal["rc"] == 0, normal
        assert normal["stdout"] == "hello\n", normal
        assert normal["stderr"] == "warn", normal
        assert "__MMBT_EXEC_SID_" not in normal["stderr"], normal
        assert timed["rc"] == -1, timed
        assert "timeout after 2s" in timed["stderr"], timed
        assert "session cleanup: session=" in timed["stderr"], timed
        assert "time.sleep(60)" not in top, top
        assert "timeout 60" not in top, top

        print(json.dumps({"normal": normal, "timed": timed}, indent=2))
        print(top.rstrip())
    finally:
        subprocess.run(
            ["docker", "rm", "-f", container],
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    main()
