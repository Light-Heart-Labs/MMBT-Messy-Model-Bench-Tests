#!/usr/bin/env python3
r"""Unit tests for the D3 fix: p2_triage v2 grader + v2 ground truth + v2 brief.

D3 (grader-defects.md): the v1 brief defined urgency `n/a` "for noise/spam
where urgency doesn't apply" but the v1 ground truth never used `n/a` (spam
tickets 004/009/021 were `low`), and ticket 029 (extortion) was
`security-incident`/`urgent` while the brief's rules-of-the-road said
extortion threats are `spam-or-noise`. 64 of 64 prior-corpus cells followed
the brief on all four tickets and were penalised for it. The v2 ground truth
credits the brief-compliant answers; the v2 grader parses the urgency
vocabulary from the v2 brief and validates both sides against it.

Runnable as `python3 -m pytest` or plain `python3 test_d3_triage_v2.py`.
"""
from __future__ import annotations

import copy
import importlib.util
import json
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


tg = _load("v2_triage_grade", V2DIR / "phase2_triage_grade.py")

BRIEF_V2 = REPO / "tooling" / "tasks" / "v2" / "task_triage.md"
GT_V2 = V2DIR / "ground_truth" / "phase2_triage.json"


def _gt() -> dict:
    return json.loads(GT_V2.read_text(encoding="utf-8"))


def _agent_from_gt(gt: dict) -> dict:
    """A brief-compliant agent output that matches the v2 ground truth exactly."""
    return {
        "tickets": {
            tid: {"category": lbl["category"], "urgency": lbl["urgency"], "duplicate_of": None}
            for tid, lbl in gt["tickets"].items()
        },
        "summary": {
            "duplicate_clusters": gt["summary"]["duplicate_clusters"],
        },
    }


def _grade(agent: dict) -> dict:
    with tempfile.TemporaryDirectory() as td:
        ws = Path(td) / "ws"
        ws.mkdir()
        (ws / "triage_results.json").write_text(json.dumps(agent), encoding="utf-8")
        return tg.grade(ws, GT_V2, BRIEF_V2)


# ------------------------------------------------------------ vocabulary parse

def test_vocab_parsed_from_v2_brief():
    vocab = tg.parse_urgency_vocab(BRIEF_V2)
    assert vocab == ["urgent", "normal", "low", "n/a"]


def test_parse_rejects_brief_without_urgency_section():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "brief.md"
        p.write_text("# A brief\n\nNo urgency section here.\n", encoding="utf-8")
        try:
            tg.parse_urgency_vocab(p)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError for missing urgency section")


# --------------------------------------------------- fixture consistency (D3)

def test_v2_ground_truth_credits_na_for_spam_trio():
    gt = _gt()
    for tid in ("004", "009", "021"):
        assert gt["tickets"][tid]["category"] == "spam-or-noise", tid
        assert gt["tickets"][tid]["urgency"] == "n/a", tid


def test_v2_ground_truth_resolves_029_to_brief_reading():
    gt = _gt()
    assert gt["tickets"]["029"]["category"] == "spam-or-noise"
    assert gt["tickets"]["029"]["urgency"] == "n/a"
    assert gt["summary"]["by_category"]["spam-or-noise"] == 4
    assert gt["summary"]["by_category"]["security-incident"] == 1
    assert gt["summary"]["urgent_count"] == 6


def test_v2_gt_urgencies_all_within_brief_vocab():
    vocab = set(tg.parse_urgency_vocab(BRIEF_V2))
    gt = _gt()
    for tid, lbl in gt["tickets"].items():
        assert lbl["urgency"] in vocab, (tid, lbl["urgency"])


def test_v2_brief_is_internally_consistent_on_extortion():
    text = BRIEF_V2.read_text(encoding="utf-8")
    gloss = next(line for line in text.splitlines() if line.startswith("- `security-incident`"))
    assert "extortion" not in gloss.lower()
    noise_rule = next(line for line in text.splitlines() if "Be skeptical of obvious noise" in line)
    assert "extortion" in noise_rule.lower()
    assert "spam-or-noise" in noise_rule


# --------------------------------------------------------------- grading (D3)

def test_brief_compliant_agent_scores_perfect_and_passes():
    r = _grade(_agent_from_gt(_gt()))
    assert r["scores"]["category_accuracy"] == 1.0
    assert r["scores"]["urgency_accuracy"] == 1.0
    assert r["scores"]["duplicate_recall"] == 1.0
    assert r["verdict"] == "PASS"
    assert r["errors"]["urgency_errors"] == []
    assert r["errors"]["invalid_urgency_labels"] == []
    assert r["urgency_vocabulary"]["labels"] == ["urgent", "normal", "low", "n/a"]


def test_prior_corpus_universal_answers_no_longer_penalised():
    # Every prior-corpus cell answered n/a on 004/009/021 and
    # spam-or-noise/n/a on 029; under v1 fixtures that cost a constant
    # 0.133 urgency / 0.033 category. Under v2 those answers are simply
    # correct: an agent can drop 4 OTHER urgencies and still clear 0.70.
    gt = _gt()
    agent = _agent_from_gt(gt)
    for tid in ("001", "005", "010", "017"):  # unrelated tickets, wrong urgency
        agent["tickets"][tid]["urgency"] = "low" if gt["tickets"][tid]["urgency"] != "low" else "normal"
    r = _grade(agent)
    assert r["scores"]["urgency_accuracy"] == round(26 / 30, 3)
    assert r["verdict"] == "PASS"
    flagged = {e["id"] for e in r["errors"]["urgency_errors"]}
    assert flagged.isdisjoint({"004", "009", "021", "029"})


def test_out_of_vocab_agent_label_is_flagged_and_counted():
    agent = _agent_from_gt(_gt())
    agent["tickets"]["001"]["urgency"] = "critical"  # not in the brief vocabulary
    r = _grade(agent)
    assert r["scores"]["urgency_accuracy"] == round(29 / 30, 3)
    assert r["errors"]["invalid_urgency_labels"] == [{"id": "001", "predicted": "critical"}]
    assert any(e["id"] == "001" for e in r["errors"]["urgency_errors"])


def test_out_of_vocab_ground_truth_aborts():
    # The grader must refuse to grade against a fixture that contradicts the
    # brief vocabulary — the exact defect class D3 was.
    gt = _gt()
    gt["tickets"]["004"]["urgency"] = "whenever"
    with tempfile.TemporaryDirectory() as td:
        bad_gt = Path(td) / "gt.json"
        bad_gt.write_text(json.dumps(gt), encoding="utf-8")
        ws = Path(td) / "ws"
        ws.mkdir()
        (ws / "triage_results.json").write_text(
            json.dumps(_agent_from_gt(_gt())), encoding="utf-8"
        )
        try:
            tg.grade(ws, bad_gt, BRIEF_V2)
        except ValueError as e:
            assert "whenever" in str(e)
        else:
            raise AssertionError("expected ValueError for out-of-vocab ground truth")


def test_grade_records_brief_and_gt_hashes():
    r = _grade(_agent_from_gt(_gt()))
    assert r["urgency_vocabulary"]["source_brief"].endswith("task_triage.md")
    assert len(r["urgency_vocabulary"]["source_brief_sha256"]) == 64
    assert len(r["inputs"]["ground_truth_sha256"]) == 64


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
