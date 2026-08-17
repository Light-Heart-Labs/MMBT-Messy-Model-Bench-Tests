#!/usr/bin/env python3
"""Deterministic end-to-end delivery validator (PREREGISTRATION.md section 4).

Primary outcome, mechanically decided — existence/schema, never quality:

  delivery := (finish_reason == "done_signal")            # model's own done()
              AND summary.json present + parses
              AND workspace_final.tar.gz present + readable
              AND every per-family expected artifact exists in the final
                  workspace tarball and passes its schema kind

Also assigns a mechanical ``classification`` used by the campaign runner's
infra-rerun ledger. The delivery flag and the loop flag are DISTINCT columns
(protocol section 4); this tool never reads loop metrics.

Classifications:
  delivered              delivery == true
  completed-no-delivery  cell ended on its own terms but delivery == false
                         (model_stopped, stuck detector, token cap, missing
                         artifacts, ...)
  loop-terminated        label.json primary in {loop-run30, identical-call-loop}
  timeout                label.json primary == timeout
  context-exhausted      api_error finish whose recorded transcript error is
                         the serving engine's HTTP 400
                         exceed_context_size_error AND the transcript has at
                         least one model turn: the model's own prompt growth
                         exhausted the serving context window. MODEL outcome
                         (DEVIATIONS.md deviation 1) — terminal like a
                         loop-label cell: delivery false, never quarantined,
                         never rerun.
  infra                  mechanical infrastructure failure: any other
                         api_error finish (connection refused/reset, 5xx,
                         timeout, empty response), missing/empty transcript,
                         or no terminal evidence at all -> quarantine +
                         same-seed rerun (ledgered)

stdlib only.
"""

import argparse
import io
import json
import re
import sys
import tarfile
from pathlib import Path

KNOWN_FAMILIES = [
    "p1_bugfix", "p1_testwrite", "p1_refactor",
    "p2_extract", "p2_ci", "p2_hallucination", "p2_triage",
    "p3_doc", "p3_business", "p3_market", "p3_writing", "p3_pm",
]

LOOP_LABELS = ("loop-run30", "identical-call-loop")
MAX_JSON_MEMBER_BYTES = 50 * 1024 * 1024

# llama-server rejects a request whose prompt outgrew the serving window with
# HTTP 400 {"error": {"type": "exceed_context_size_error", "message":
# "request (N tokens) exceeds the available context size (M tokens), ..."}}.
# Matched mechanically on either the error type string or the token-count
# message so the classification survives message-wording drift.
CONTEXT_EXHAUSTION_MARKER = "exceed_context_size"
CONTEXT_EXHAUSTION_RE = re.compile(
    r"request \(\d+ tokens?\) exceeds the (?:available )?context size \(\d+ tokens?\)")


def family_from_run_name(run_name):
    for fam in sorted(KNOWN_FAMILIES, key=len, reverse=True):
        if run_name.startswith(fam + "_"):
            return fam
    return None


def load_json(path):
    try:
        return json.loads(Path(path).read_text()), None
    except FileNotFoundError:
        return None, "missing"
    except (json.JSONDecodeError, OSError) as e:
        return None, f"unreadable: {type(e).__name__}: {e}"


def transcript_model_events(transcript_path):
    """Count of type=="model" events; None if transcript missing."""
    p = Path(transcript_path)
    if not p.exists():
        return None
    n = 0
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("type") == "model":
                n += 1
    return n


def transcript_last_error(transcript_path):
    """Last type=="error" event dict; None if none or transcript missing."""
    p = Path(transcript_path)
    if not p.exists():
        return None
    last = None
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("type") == "error":
                last = ev
    return last


def error_is_context_exhaustion(error_event):
    """True when a recorded api_error event is the serving engine's HTTP 400
    exceed_context_size_error (the prompt outgrew the context window).

    Context exhaustion through the model's own prompt growth is MODEL
    behaviour, not an infrastructure failure (DEVIATIONS.md deviation 1):
    quarantine is reserved for mechanically identified infrastructure
    failures, so this must NOT classify as infra.
    """
    if not isinstance(error_event, dict):
        return False
    text = " ".join(str(error_event.get(k) or "") for k in ("error", "body"))
    return (CONTEXT_EXHAUSTION_MARKER in text
            or bool(CONTEXT_EXHAUSTION_RE.search(text)))


class TarIndex:
    """Normalized member index over workspace_final.tar.gz ("./x" -> "x")."""

    def __init__(self, tar_path):
        self.tar_path = Path(tar_path)
        self.files = {}   # normalized name -> TarInfo
        self.dirs = set()
        self.error = None
        try:
            self.tf = tarfile.open(self.tar_path, "r:gz")
        except (OSError, tarfile.TarError) as e:
            self.tf = None
            self.error = f"{type(e).__name__}: {e}"
            return
        for m in self.tf.getmembers():
            name = m.name
            if name.startswith("./"):
                name = name[2:]
            name = name.strip("/")
            if not name:
                continue
            if m.isdir():
                self.dirs.add(name)
            elif m.isfile():
                self.files[name] = m
            # every parent of any member is a directory
            parts = name.split("/")
            for i in range(1, len(parts)):
                self.dirs.add("/".join(parts[:i]))

    def close(self):
        if self.tf is not None:
            self.tf.close()

    def dir_nonempty(self, path):
        prefix = path.rstrip("/") + "/"
        return any(f.startswith(prefix) for f in self.files) or \
            any(d.startswith(prefix) for d in self.dirs)

    def file_ok(self, path):
        m = self.files.get(path)
        return m is not None and m.size > 0

    def read_file(self, path):
        m = self.files.get(path)
        if m is None or m.size > MAX_JSON_MEMBER_BYTES:
            return None
        fh = self.tf.extractfile(m)
        return fh.read() if fh else None

    def basename_matches(self, basename):
        return [f for f in self.files if f.split("/")[-1] == basename]


def check_artifact(idx, spec):
    """One artifact spec -> (ok, reason_or_None).

    Spec forms:
      {"path": "CHANGELOG.md", "kind": "file"|"md"|"json"|"dir"}
      {"basename": "decisions.md", "kind": "file"}     # anywhere in the tree
      {"anyof": [spec, spec, ...]}                      # first match wins
    """
    if "anyof" in spec:
        reasons = []
        for s in spec["anyof"]:
            ok, why = check_artifact(idx, s)
            if ok:
                return True, None
            reasons.append(why)
        return False, "none of: " + "; ".join(reasons)

    kind = spec.get("kind", "file")
    if "basename" in spec:
        hits = idx.basename_matches(spec["basename"])
        hits = [h for h in hits if idx.file_ok(h)]
        if not hits:
            return False, f"no non-empty file named {spec['basename']!r} anywhere"
        if kind == "json":
            for h in hits:
                data = idx.read_file(h)
                try:
                    json.loads(data)
                    return True, None
                except (TypeError, ValueError):
                    continue
            return False, f"{spec['basename']!r} found but no copy parses as JSON"
        return True, None

    path = spec["path"].strip("/")
    if kind == "dir":
        if path in idx.dirs and idx.dir_nonempty(path):
            return True, None
        if path in idx.dirs:
            return False, f"dir {path!r} exists but is empty"
        return False, f"dir {path!r} missing"
    if not idx.file_ok(path):
        return False, f"file {path!r} missing or empty"
    if kind == "json":
        data = idx.read_file(path)
        try:
            json.loads(data)
        except (TypeError, ValueError) as e:
            return False, f"file {path!r} is not valid JSON ({type(e).__name__})"
    return True, None


def load_artifacts_config(path):
    cfg, err = load_json(path)
    if err:
        raise SystemExit(f"artifacts config {path}: {err}")
    return cfg


def validate_cell(cell_dir, family=None, artifacts_spec=None):
    """Validate one cell log dir. Returns the per-cell result dict."""
    cell_dir = Path(cell_dir)
    run_name = cell_dir.name
    family = family or family_from_run_name(run_name)
    reasons = []

    summary, summary_err = load_json(cell_dir / "summary.json")
    label, _ = load_json(cell_dir / "label.json")
    receipt, receipt_err = load_json(cell_dir / "receipt.json")
    model_events = transcript_model_events(cell_dir / "transcript.jsonl")
    finish_reason = (summary or {}).get("finish_reason")
    label_primary = (label or {}).get("primary")

    # --- delivery flag (protocol section 4, existence/schema only) ---
    done_signal = finish_reason == "done_signal"
    if summary_err:
        reasons.append(f"summary.json {summary_err}")
    elif not done_signal:
        reasons.append(f"finish_reason is {finish_reason!r}, not the model's own done() signal")

    tar_path = cell_dir / "workspace_final.tar.gz"
    artifacts_ok = False
    if not tar_path.exists():
        reasons.append("workspace_final.tar.gz missing")
    else:
        idx = TarIndex(tar_path)
        if idx.error:
            reasons.append(f"workspace_final.tar.gz unreadable: {idx.error}")
        else:
            artifacts_ok = True
            spec = (artifacts_spec or {}).get(family) if family else None
            if spec is None:
                reasons.append(f"no expected-artifact list for family {family!r} (config gap)")
                artifacts_ok = False
            else:
                for item in spec:
                    ok, why = check_artifact(idx, item)
                    if not ok:
                        artifacts_ok = False
                        reasons.append(f"artifact: {why}")
            idx.close()

    delivery = bool(done_signal and not summary_err and tar_path.exists() and artifacts_ok)

    # --- mechanical classification for the runner/ledger ---
    if label_primary in LOOP_LABELS:
        classification = "loop-terminated"
    elif label_primary == "timeout":
        classification = "timeout"
    elif isinstance(finish_reason, str) and finish_reason.startswith("api_error"):
        if model_events and error_is_context_exhaustion(
                transcript_last_error(cell_dir / "transcript.jsonl")):
            # Model outcome, terminal like a loop-label cell: delivery stays
            # false, no quarantine, no rerun (DEVIATIONS.md deviation 1).
            # A zero-model-turn context overflow is NOT this bucket: the
            # prompt can only outgrow the window through model turns, so a
            # first-request overflow is a config/infra problem and falls
            # through to infra below.
            classification = "context-exhausted"
            reasons.append(
                f"model: prompt growth exhausted the serving context window ({finish_reason})")
        else:
            classification = "infra"
            reasons.append(f"infra: {finish_reason}")
    elif model_events is None or model_events == 0:
        classification = "infra"
        reasons.append("infra: transcript missing or has zero model turns")
    elif summary is None:
        classification = "infra"
        reasons.append("infra: no summary.json and no terminal label — harness died without a verdict")
    elif delivery:
        classification = "delivered"
    else:
        classification = "completed-no-delivery"

    return {
        "run_name": run_name,
        "cell_dir": str(cell_dir),
        "family": family,
        "delivery": delivery,
        "reasons": reasons,
        "classification": classification,
        "finish_reason": finish_reason,
        "label_primary": label_primary,
        "model_turns": model_events,
        "receipt_present": receipt is not None,
        "receipt_error": receipt_err,
        "infra_rerun_eligible": classification == "infra",
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cells", nargs="+", help="cell log dirs (logs/<run_name>)")
    ap.add_argument("--family", default=None,
                    help="override family (default: parsed from run name)")
    ap.add_argument("--artifacts-config", default=None,
                    help="family_artifacts.json (default: alongside this script "
                         "in configs/family_artifacts.json)")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()

    cfg_path = args.artifacts_config or str(
        Path(__file__).resolve().parent / "configs" / "family_artifacts.json")
    artifacts_spec = load_artifacts_config(cfg_path)

    worst = 0
    for cell in args.cells:
        out = validate_cell(cell, family=args.family, artifacts_spec=artifacts_spec)
        print(json.dumps(out, indent=2 if args.pretty else None))
        if not out["delivery"]:
            worst = max(worst, 1)
    return worst


if __name__ == "__main__":
    sys.exit(main())
