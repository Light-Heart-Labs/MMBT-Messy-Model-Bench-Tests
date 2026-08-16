#!/usr/bin/env python3
r"""Unit tests for the D1 fix across the four length-gated v2 graders.

Each grader must (a) accept a deliverable inside the +-3% band above the
ceiling, (b) reject one beyond the band, and (c) — the D1 signature — accept a
deliverable that the v1 regex counter would have rejected (hyphenated
compounds double-count under the regex but count once under wc -w).

Runnable as `python3 -m pytest` or plain `python3 test_d1_length_gates.py`.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import tempfile
from pathlib import Path

V2DIR = Path(__file__).resolve().parents[1]
if str(V2DIR) not in sys.path:
    sys.path.insert(0, str(V2DIR))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


bm = _load("v2_business_memo_grade", V2DIR / "phase3_business_memo_grade.py")
ds = _load("v2_doc_synthesis_grade", V2DIR / "phase3_doc_synthesis_grade.py")
we = _load("v2_writing_editing_grade", V2DIR / "phase3_writing_editing_grade.py")
pm = _load("v2_project_mgmt_grade", V2DIR / "phase3_project_mgmt_grade.py")


def _pad(n: int) -> str:
    return " ".join(["pad"] * n)


def _hyphen_pad(n: int) -> str:
    # each token counts 1 under wc -w and 2 under the v1 regex
    return " ".join(["cost-benefit"] * n)


# ---------------------------------------------------------------- business memo

BM_CONTENT = (
    "Recommendation: hold. Do not proceed until the concerns below are resolved.\n"
    "The runway math is inconsistent and relies on a stale burn rate.\n"
    "Customer quotes look curated — a cherry-pick of 5 customers.\n"
    "Logo churn of 9% is buried in an appendix.\n"
    "The $3.2m synergy figure is asserted without supporting analysis.\n"
    "No build vs buy alternative was considered.\n"
)

BM_PLANTED = {
    "planted_signals_a_careful_reader_should_flag": {
        "B1_runway_math_is_inconsistent": {"summary": "runway math inconsistent"},
        "B2_customer_quotes_curated": {"summary": "customer quotes curated"},
        "B3_logo_retention_buried": {"summary": "logo retention buried"},
        "B4_arr_growth_reframed": {"summary": "arr growth reframed"},
        "B5_comparable_transactions_cherry_picked": {"summary": "comps cherry picked"},
        "B6_integration_synergy_unverified": {"summary": "synergy unverified"},
        "B7_no_competitive_alternative_analysis": {"summary": "no build-vs-buy"},
        "B8_authorship_and_signoff_skewed": {"summary": "signoff skewed"},
    }
}


def _bm_grade(td: Path, memo_text: str) -> dict:
    ws = td / "ws"
    ws.mkdir(exist_ok=True)
    (ws / "memo.md").write_text(memo_text, encoding="utf-8")
    planted = td / "planted.json"
    planted.write_text(json.dumps(BM_PLANTED), encoding="utf-8")
    return bm.grade(ws, planted)


def test_business_memo_within_band_passes():
    with tempfile.TemporaryDirectory() as td:
        # content ~60 wc-words; pad to ~710 (over 700, inside 721 band)
        r = _bm_grade(Path(td), BM_CONTENT + _pad(650))
        assert 700 < r["scores"]["memo_word_count"] <= 721
        assert r["scores"]["memo_within_word_limit"] is True
        assert r["verdict"] == "PASS", r


def test_business_memo_beyond_band_fails():
    with tempfile.TemporaryDirectory() as td:
        r = _bm_grade(Path(td), BM_CONTENT + _pad(680))
        assert r["scores"]["memo_word_count"] > 721
        assert r["verdict"] == "FAIL"


def test_business_memo_d1_signature_regex_over_wc_under():
    # v1 regex counts each "cost-benefit" as 2 words and would gate this out;
    # wc -w counts it once and the deliverable is under the ceiling.
    text = BM_CONTENT + _hyphen_pad(600)
    with tempfile.TemporaryDirectory() as td:
        r = _bm_grade(Path(td), text)
        assert len(re.findall(r"\b\w+\b", text)) > 721  # v1 counter would reject
        assert r["scores"]["memo_word_count"] <= 700    # wc -w is under the raw cap
        assert r["verdict"] == "PASS", r


# ---------------------------------------------------------------- doc synthesis

DS_FACTS = {
    "facts": {
        f"F{i}": {"summary": f"fact {i}", "match_keywords_any": [f"factkeyword{i}"]}
        for i in range(1, 7)
    }
}
DS_CONTENT = "Recommend more diligence. " + " ".join(f"factkeyword{i}" for i in range(1, 7)) + "\n"


def _ds_grade(td: Path, brief_text: str) -> dict:
    ws = td / "ws"
    ws.mkdir(exist_ok=True)
    (ws / "brief.md").write_text(brief_text, encoding="utf-8")
    kf = td / "facts.json"
    kf.write_text(json.dumps(DS_FACTS), encoding="utf-8")
    return ds.grade(ws, kf)


def test_doc_synthesis_within_band_passes():
    with tempfile.TemporaryDirectory() as td:
        r = _ds_grade(Path(td), DS_CONTENT + _pad(705))
        assert 700 < r["scores"]["word_count"] <= 721
        assert r["verdict"] == "PASS", r


def test_doc_synthesis_beyond_band_fails():
    with tempfile.TemporaryDirectory() as td:
        r = _ds_grade(Path(td), DS_CONTENT + _pad(730))
        assert r["scores"]["word_count"] > 721
        assert r["verdict"] == "FAIL"


# -------------------------------------------------------------- writing/editing

WE_SPEC = {
    "audiences": {
        "ceo_brief": {"filename": "ceo_brief.md", "max_words": 250},
    }
}
WE_CONTENT = (
    "Outage incident summary: 11,400 accounts were impacted, the second event "
    "in 90 days.\n"
)


def _we_grade(td: Path, text: str) -> dict:
    ws = td / "ws"
    ws.mkdir(exist_ok=True)
    (ws / "ceo_brief.md").write_text(text, encoding="utf-8")
    spec = td / "audience_briefs.json"
    spec.write_text(json.dumps(WE_SPEC), encoding="utf-8")
    return we.grade(ws, spec)


def test_writing_editing_within_band_passes():
    with tempfile.TemporaryDirectory() as td:
        # content is 13 wc-words; pad to 252 (over 250, inside 257 band)
        r = _we_grade(Path(td), WE_CONTENT + _pad(239))
        aud = r["per_audience"]["ceo_brief"]
        assert 250 < aud["word_count"] <= 257, aud
        assert aud["within_word_limit"] is True
        assert r["verdict"] == "PASS", r


def test_writing_editing_beyond_band_fails():
    with tempfile.TemporaryDirectory() as td:
        r = _we_grade(Path(td), WE_CONTENT + _pad(340))
        aud = r["per_audience"]["ceo_brief"]
        assert aud["word_count"] > 257
        assert r["verdict"] == "FAIL"


# --------------------------------------------------------------- project mgmt

PM_CONTENT = (
    "# Status Report\n"
    "## Headline\nAurora V1 is on track with three material risks.\n"
    "## Workstreams\n"
    "- WS1 query layer (owner: Dana) — on track\n"
    "- WS2 dashboard refresh — on track\n"
    "- WS3 panel density architectural fix — at risk\n"
    "- WS4 access control (IAM) — blocking V1\n"
    "## Risks\n"
    "- High: timeline slip on IAM (week 5)\n"
    "- High: legal unresponsive on the private-beta contract (week 6)\n"
    "- Medium: 40-panel limit expectation mismatch (week 4)\n"
    "## Decisions made\n"
    "- Week 3: branding deferred to v1.5\n"
    "- Week 4: option b private beta\n"
    "## Milestones\n"
    "- mid-may: query layer complete\n"
    "- mid-july: V1 launch\n"
    "- v1.5: custom branding (deferred)\n"
)


def _pm_grade(td: Path, text: str) -> dict:
    ws = td / "ws"
    ws.mkdir(exist_ok=True)
    (ws / "status_report.md").write_text(text, encoding="utf-8")
    expected = td / "expected.json"
    expected.write_text("{}", encoding="utf-8")
    return pm.grade(ws, expected)


def test_project_mgmt_within_band_passes():
    with tempfile.TemporaryDirectory() as td:
        base = _pm_grade(Path(td), PM_CONTENT)
        base_wc = base["scores"]["word_count"]
        assert base["verdict"] == "PASS", base
        r = _pm_grade(Path(td), PM_CONTENT + _pad(710 - base_wc))
        assert 700 < r["scores"]["word_count"] <= 721
        assert r["verdict"] == "PASS", r


def test_project_mgmt_beyond_band_fails():
    with tempfile.TemporaryDirectory() as td:
        r = _pm_grade(Path(td), PM_CONTENT + _pad(730))
        assert r["scores"]["word_count"] > 721
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
