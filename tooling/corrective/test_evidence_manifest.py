#!/usr/bin/env python3
"""Unit tests for the evidence manifest grid + fixed-N balance checker."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import evidence_manifest as em  # noqa: E402

CFG = {
    "arm": "official-nothink",
    "thinking": "off",
    "sampler": {"benchmark_temperature": 0.7, "benchmark_top_p": 0.8,
                "benchmark_top_k": 20, "benchmark_min_p": 0.0,
                "benchmark_presence_penalty": 1.5, "benchmark_repeat_penalty": 1.0},
    "seeds": [101, 211, 307, 401, 503, 601],
    "families": ["p1_bugfix", "p2_extract", "p3_pm"],
    "models": {
        "q38": {"alias": "Qwen3.8-27B-UD-Q4_K_XL", "label": "q38-official-nothink"},
        "q36": {"alias": "Qwen3.6-27B-UD-Q4_K_XL", "label": "q36-official-nothink"},
    },
    "host_plan": {
        "phase_a": {"seeds": [101, 211, 307],
                    "q38": {"tower": "tower1", "port": 18101},
                    "q36": {"tower": "tower3", "port": 18103}},
        "phase_b": {"seeds": [401, 503, 601],
                    "q38": {"tower": "tower3", "port": 18103},
                    "q36": {"tower": "tower1", "port": 18101}},
    },
    "quant": "UD-Q4_K_XL",
    "loop_threshold": 30,
}


class TestGrid(unittest.TestCase):
    def test_expected_grid_size_and_crossover(self):
        cells = list(em.expected_cells(CFG))
        self.assertEqual(len(cells), 3 * 6 * 2)
        keys = {(c["family"], c["seed"], c["model_key"]) for c in cells}
        self.assertEqual(len(keys), len(cells), "duplicate expected cells")
        by = {(c["seed"], c["model_key"]): c["planned_host"] for c in cells}
        # crossover: q38 on tower1 for 101/211/307, tower3 for 401/503/601
        self.assertEqual(by[(101, "q38")], "tower1")
        self.assertEqual(by[(101, "q36")], "tower3")
        self.assertEqual(by[(503, "q38")], "tower3")
        self.assertEqual(by[(503, "q36")], "tower1")

    def test_run_names_encode_label_and_seed(self):
        cells = list(em.expected_cells(CFG))
        names = {c["run_name"] for c in cells}
        self.assertIn("p2_extract_q38-official-nothink-s101_v1", names)
        self.assertIn("p3_pm_q36-official-nothink-s601_v1", names)

    def test_model_level_quant_overrides_arm_quant(self):
        # quant pilot: per-model quant; absent model key falls back to
        # the arm-level value (default-preserving for existing configs).
        cfg = json.loads(json.dumps(CFG))
        cfg["models"]["q38"]["quant"] = "Q8_0"
        quants = {c["model_key"]: c["quant"] for c in em.expected_cells(cfg)}
        self.assertEqual(quants["q38"], "Q8_0")
        self.assertEqual(quants["q36"], "UD-Q4_K_XL")


class TestBalance(unittest.TestCase):
    def run_check(self, rows, cfg=CFG):
        with tempfile.TemporaryDirectory() as d:
            cfg_path = Path(d) / "cfg.json"
            cfg_path.write_text(json.dumps(cfg))
            man = Path(d) / "manifest.jsonl"
            with open(man, "w") as f:
                for r in rows:
                    f.write(json.dumps(r) + "\n")
            proc = subprocess.run(
                [sys.executable, str(HERE / "evidence_manifest.py"), "check",
                 "--config", str(cfg_path), "--manifest", str(man)],
                capture_output=True, text=True)
            return proc.returncode, json.loads(proc.stdout)

    def full_rows(self):
        return [{"arm": c["arm"], "family": c["family"], "seed": c["seed"],
                 "model_key": c["model_key"], "status": "present"}
                for c in em.expected_cells(CFG)]

    def test_complete_grid_is_balanced(self):
        rc, report = self.run_check(self.full_rows())
        self.assertEqual(rc, 0, report)
        self.assertTrue(report["balanced"])
        self.assertEqual(report["expected_cells"], 36)

    def test_missing_cell_fails(self):
        rows = self.full_rows()[:-1]
        rc, report = self.run_check(rows)
        self.assertEqual(rc, 1)
        self.assertEqual(len(report["missing"]), 1)

    def test_duplicate_cell_fails(self):
        rows = self.full_rows()
        rows.append(dict(rows[0]))
        rc, report = self.run_check(rows)
        self.assertEqual(rc, 1)
        self.assertEqual(len(report["duplicates"]), 1)

    def test_unexpected_cell_fails(self):
        rows = self.full_rows()
        rows.append({"arm": "official-nothink", "family": "p2_extract",
                     "seed": 999, "model_key": "q38", "status": "present"})
        rc, report = self.run_check(rows)
        self.assertEqual(rc, 1)
        self.assertEqual(len(report["unexpected"]), 1)

    def test_missing_status_rows_do_not_count_as_present(self):
        rows = self.full_rows()
        rows[0]["status"] = "missing"
        rc, report = self.run_check(rows)
        self.assertEqual(rc, 1)
        self.assertEqual(len(report["missing"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
