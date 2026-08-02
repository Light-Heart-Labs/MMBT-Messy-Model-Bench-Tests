#!/usr/bin/env python3
import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).with_name("correct_gemma4_project_mgmt_grades.py")
SPEC = importlib.util.spec_from_file_location("pm_correction", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def raw_grade():
    return {
        "verdict": "FAIL",
        "scores": {
            "sections_present": ["workstream", "risk", "decision", "milestone"],
            "word_count": 300,
        },
        "thresholds": {
            "min_workstreams": 4,
            "min_risks": 3,
            "min_decisions": 3,
            "min_milestones": 3,
            "max_word_count": 700,
        },
        "details": {
            "workstreams": {f"WS{i}": {"matched": True} for i in range(1, 7)},
            "risks": {
                "R1": {"matched": False}, "R2": {"matched": False},
                "R3": {"matched": False}, "R4": {"matched": True},
                "R5": {"matched": True}, "R6": {"matched": False},
            },
            "decisions": {
                "D1_branding": {"matched": True},
                "D2_panel_limit": {"matched": True},
                "D3_mobile": {"matched": False},
                "D4_option_b": {"matched": False},
            },
            "milestones": {f"M{i}": {"matched": True} for i in range(1, 6)},
        },
    }


def test_semantic_equivalents_correct_only_the_known_lexical_misses():
    report = """
    Risks: Maevia was promised GA and may push back on private beta.
    Legal has not yet responded to the private-beta contract draft.
    Decisions: web-responsive in V1; native in V2.
    SDK release changed to private beta (3-5 customers).
    """
    corrected, changes = MODULE.apply_correction(raw_grade(), report)
    assert corrected["verdict"] == "PASS"
    assert corrected["scores"]["risk_recall"] == "4/6"
    assert corrected["scores"]["decision_recall"] == "4/4"
    assert {change["item"] for change in changes} == {
        "R2", "R3", "D3_mobile", "D4_option_b",
    }


def test_unrelated_text_does_not_change_a_failure():
    corrected, changes = MODULE.apply_correction(raw_grade(), "No additional evidence.")
    assert corrected["verdict"] == "FAIL"
    assert changes == []
