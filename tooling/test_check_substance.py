#!/usr/bin/env python3
import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).parent / "scripts" / "check_substance.py"
SPEC = importlib.util.spec_from_file_location("check_substance", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_command_template_digit_strips_valid_commands():
    entry = {"args": {"command": "sed -n '100,160p' report.md"}}
    assert MODULE.command_template(entry) == "sed -n '#,#p' report.md"


def test_command_template_preserves_malformed_boolean_without_crashing():
    assert MODULE.command_template({"args": {"command": True}}) == \
        "<invalid-command:bool:true>"


def test_command_template_handles_non_mapping_args_without_crashing():
    assert MODULE.command_template({"args": ["unexpected"]}) == \
        "<invalid-args:list>"
