#!/usr/bin/env python3
import importlib.util
import os
from pathlib import Path


os.environ["GEMMA_EXTENDED_LANE_INDEX"] = "0"
os.environ["GEMMA_EXTENDED_LANE_COUNT"] = "2"
os.environ["GEMMA_EXTENDED_PORT"] = "8000"
SCRIPT = Path(__file__).with_name("run_gemma4_extended_suites.py")
SPEC = importlib.util.spec_from_file_location("runner", SCRIPT)
RUNNER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(RUNNER)


def test_names_are_campaign_specific_and_replicated():
    assert RUNNER.run_name("dreamserver-1-pr-audit", 2) == "n1_gemma4-31b-q4_v2"
    assert RUNNER.run_name("wallstreet-board-presentation", 3) == "gemma4-31b-q4_board_pres_v3"


def test_harness_command_pins_lane_and_full_operating_point():
    suite = {
        "id": "dreamserver-1-pr-audit",
        "task": "tooling/tasks/task_pr_audit_n1.md",
        "temperature": 1.0,
        "stuck_threshold": 500,
        "max_output_tokens_cap": 262144,
        "require_git_tag": True,
    }
    command = RUNNER.harness_command(suite, 1, 262144, 0.95, 64)
    joined = " ".join(command)
    assert "--port 8000" in joined
    assert "--max-model-len 262144" in joined
    assert "--max-output-tokens-cap 262144" in joined
    assert "--temperature 1.0 --top-p 0.95 --top-k 64" in joined
    assert "--serving-manifest" in command
    assert "--require-git-tag" in command
