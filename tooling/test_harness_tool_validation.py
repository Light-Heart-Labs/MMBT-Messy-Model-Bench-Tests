#!/usr/bin/env python3
import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).with_name("harness.py")
SPEC = importlib.util.spec_from_file_location("harness", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def execute(name, args):
    return MODULE.execute_tool(name, args, Path("/tmp/not-used"))


def test_missing_required_arguments_are_recoverable_tool_errors():
    assert execute("read_file", {}) == "TOOL_ERROR: read_file missing required argument(s): path"
    assert execute("write_file", {"path": "x"}) == (
        "TOOL_ERROR: write_file missing required argument(s): content"
    )
    assert execute("bash", {}) == "TOOL_ERROR: bash missing required argument(s): command"


def test_malformed_argument_types_are_recoverable_tool_errors():
    assert execute("read_file", {"path": None}) == (
        "TOOL_ERROR: read_file argument 'path' must be a non-empty string"
    )
    assert execute("write_file", {"path": "x", "content": 1}) == (
        "TOOL_ERROR: write_file argument 'content' must be a string"
    )
    assert execute("bash", {"command": "true", "timeout_s": "later"}) == (
        "TOOL_ERROR: bash argument 'timeout_s' must be a positive integer"
    )


def test_non_object_arguments_are_recoverable_tool_errors():
    assert execute("read_file", []) == "TOOL_ERROR: read_file arguments must be a JSON object"


def test_git_tag_gate_requires_clean_annotated_tag_at_head(monkeypatch):
    calls = []

    def fake_docker_exec(command, timeout):
        calls.append(command)
        return {"stdout": "TAG_FOUND\n", "stderr": "", "returncode": 0}

    monkeypatch.setattr(MODULE, "docker_exec", fake_docker_exec)
    assert MODULE.validate_done([], True) is None
    command = calls[-1]
    assert "diff --quiet" in command
    assert "diff --cached --quiet" in command
    assert "ls-files --others --exclude-standard" in command
    assert "tag --points-at HEAD" in command
    assert "cat-file -t" in command


def test_git_tag_gate_fails_closed_without_qualifying_repo(monkeypatch):
    monkeypatch.setattr(
        MODULE,
        "docker_exec",
        lambda command, timeout: {"stdout": "", "stderr": "", "returncode": 0},
    )
    error = MODULE.validate_done([], True)
    assert "no clean workspace repo with an annotated tag at HEAD" in error
