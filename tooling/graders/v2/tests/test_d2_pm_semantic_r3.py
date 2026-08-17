#!/usr/bin/env python3
r"""Unit tests for the D2 fix: semantic R3 equivalence in the v2 p3_pm grader.

The natural experiment (grader-defects.md, D2): prior-corpus cells
p3_pm_qwen36-nothink-card_v2 and _v8 wrote, verbatim,

    | **High** | Private-beta contracts unsigned | Legal has not responded to draft [wk6] |

while _v4 wrote the byte-identical row with the contraction "hasn't". Under
the v1 grader the apostrophe alone decided PASS vs FAIL (risk_recall 2/6 vs
3/6 against the >=3 threshold). The v2 grader must score both identically,
via the semantic rule adopted from tooling/correct_gemma4_project_mgmt_grades.py.

Runnable as `python3 -m pytest` or plain `python3 test_d2_pm_semantic_r3.py`.
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

V2DIR = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[4]
if str(V2DIR) not in sys.path:
    sys.path.insert(0, str(V2DIR))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


pm_v2 = _load("v2_pm_grade_d2", V2DIR / "phase3_project_mgmt_grade.py")
pm_v1 = _load("v1_pm_grade_d2", REPO / "tooling" / "graders" / "phase3_project_mgmt_grade.py")
upstream = _load("upstream_pm_correction", REPO / "tooling" / "correct_gemma4_project_mgmt_grades.py")


# Verbatim line-22 rows from the natural-experiment cells (grader-defects.md D2;
# the two uncontracted rows hash identically to d34282e4e207623e234fb9731c144e41).
ROW_UNCONTRACTED = "| **High** | Private-beta contracts unsigned | Legal has not responded to draft [wk6] |"
ROW_CONTRACTED = "| **High** | Private-beta contracts unsigned | Legal hasn't responded to draft [wk6] |"

# A report that passes every other gate and whose verdict hinges on R3
# (exactly two other risks match, so risk_recall is 2/6 without R3 and 3/6
# with it — the same knife-edge as the 64 graded prior-corpus cells).
REPORT_TEMPLATE = (
    "# Status Report\n"
    "## Headline\nAurora V1 on track; contract signature is the top risk.\n"
    "## Workstreams\n"
    "- WS1 query layer (owner: Dana) — on track\n"
    "- WS2 dashboard refresh — on track\n"
    "- WS3 panel density architectural fix — at risk\n"
    "- WS4 access control (IAM) — blocking V1\n"
    "## Risks\n"
    "| Severity | Risk | Evidence |\n"
    "| **High** | IAM timeline slip | could slip past mid-July [wk5] |\n"
    "{r3_row}\n"
    "## Decisions made\n"
    # "branding cut" (not "branding deferred") so risk R5's "deferred" keyword
    # cannot fire — exactly two non-R3 risks (R1, R4) match, keeping the
    # verdict on R3's knife edge as in the prior corpus.
    "- Week 3: branding cut from V1 scope\n"
    "- Week 4: 40-panel limit confirmed\n"
    "- Week 4: option b private beta\n"
    "## Milestones\n"
    "- mid-may: query layer complete\n"
    "- mid-july: V1 launch\n"
)


def _grade(module, r3_row: str) -> dict:
    with tempfile.TemporaryDirectory() as td:
        ws = Path(td) / "ws"
        ws.mkdir()
        (ws / "status_report.md").write_text(
            REPORT_TEMPLATE.format(r3_row=r3_row), encoding="utf-8"
        )
        expected = Path(td) / "expected.json"
        expected.write_text("{}", encoding="utf-8")
        return module.grade(ws, expected)


def test_pattern_is_adopted_verbatim_from_upstream():
    # Attribution guard: the v2 semantic rule must stay byte-identical to the
    # repository's existing correction module (RULES["R3"]).
    assert pm_v2.R3_SEMANTIC_PATTERN == upstream.RULES["R3"]["patterns"][0]


def test_uncontracted_form_matches_r3_in_v2():
    r = _grade(pm_v2, ROW_UNCONTRACTED)
    r3 = r["details"]["risks"]["R3"]
    assert r3["matched"] is True
    assert r3["keyword"] == pm_v2.R3_SEMANTIC_MARKER
    assert r["semantic_rules"]["R3"]["applied"] is True
    assert r["scores"]["risk_recall"] == "3/6"
    assert r["verdict"] == "PASS", r


def test_contracted_form_matches_r3_in_v2():
    r = _grade(pm_v2, ROW_CONTRACTED)
    r3 = r["details"]["risks"]["R3"]
    assert r3["matched"] is True
    assert r3["keyword"] == "legal hasn't"  # literal keyword still wins first
    assert r["semantic_rules"]["R3"]["applied"] is False
    assert r["verdict"] == "PASS", r


def test_natural_experiment_parity_in_v2():
    # The two phrasings must receive the same verdict and the same recalls;
    # only the word count may differ ("has not" is one word longer).
    ra = _grade(pm_v2, ROW_UNCONTRACTED)
    rb = _grade(pm_v2, ROW_CONTRACTED)
    assert ra["verdict"] == rb["verdict"] == "PASS"
    for key in ("workstream_recall", "risk_recall", "decision_recall",
                "milestone_recall", "sections_present"):
        assert ra["scores"][key] == rb["scores"][key], key
    assert ra["scores"]["word_count"] == rb["scores"]["word_count"] + 1


def test_v1_grader_flips_on_the_contraction():
    # Regression documentation: v1 scores the two byte-near-identical reports
    # differently — this is the defect v2 removes. If v1 ever stops flipping,
    # this test flags that the defect model needs re-examination.
    ra = _grade(pm_v1, ROW_UNCONTRACTED)
    rb = _grade(pm_v1, ROW_CONTRACTED)
    assert ra["details"]["risks"]["R3"]["matched"] is False
    assert rb["details"]["risks"]["R3"]["matched"] is True
    assert ra["verdict"] == "FAIL"
    assert rb["verdict"] == "PASS"


def test_not_yet_responded_variant_matches():
    row = "| **High** | Contracts unsigned | Legal has not yet responded to the private-beta draft [wk6] |"
    r = _grade(pm_v2, row)
    assert r["details"]["risks"]["R3"]["matched"] is True
    assert r["verdict"] == "PASS"


def test_semantic_rule_does_not_overfire():
    # "legal" with no delay/unresponsiveness trigger within range must not match.
    row = "| Low | Miscellaneous | Legal team attended the weekly sync and raised no issues [wk6] |"
    r = _grade(pm_v2, row)
    assert r["details"]["risks"]["R3"]["matched"] is False
    assert r["semantic_rules"]["R3"]["applied"] is False
    assert r["scores"]["risk_recall"] == "2/6"
    assert r["verdict"] == "FAIL"


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as e:
                failures += 1
                print(f"FAIL {name}: {e}")
    sys.exit(1 if failures else 0)
