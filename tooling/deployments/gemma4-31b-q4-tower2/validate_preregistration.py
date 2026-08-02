#!/usr/bin/env python3
"""Fail closed when the Gemma campaign no longer matches its preregistration."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MODEL_MANIFEST = HERE / "model-manifest.json"
TOPOLOGY = HERE / "topology-matrix.json"
MICROBENCH = ROOT / "tooling/gemma4-31b-q4-mmbt.json"
EXTENDED = ROOT / "tooling/gemma4-31b-q4-extended-matrix.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


manifest = load(MODEL_MANIFEST)
topology = load(TOPOLOGY)
microbench = load(MICROBENCH)
extended = load(EXTENDED)

require(manifest["source_revision"] == "59dde24573e7e61570dba08b18a2e1fe246955ed", "source revision drift")
for key in ("model", "multimodal_projector"):
    artifact = manifest[key]
    path = Path(artifact["path"])
    require(path.is_file(), f"missing {key}: {path}")
    require(path.stat().st_size == artifact["bytes"], f"size drift for {key}")
    require(sha256(path) == artifact["sha256"], f"SHA-256 drift for {key}")
    metadata = path.parent / ".cache/huggingface/download" / f"{path.name}.metadata"
    require(metadata.is_file(), f"missing Hugging Face metadata for {key}")
    require(metadata.read_text().splitlines()[0] == manifest["source_revision"], f"metadata revision drift for {key}")

context = manifest["model_card"]["native_context_tokens"]
sampling = {
    "temperature": manifest["model_card"]["temperature"],
    "top_p": manifest["model_card"]["top_p"],
    "top_k": manifest["model_card"]["top_k"],
}
require(context == microbench["max_model_len"] == extended["served_context_tokens"], "context mismatch across configs")
require(context == topology["mandatory_per_sequence_context_tokens"], "topology context mismatch")
require(microbench["benchmark_temperature"] == sampling["temperature"], "microbench temperature drift")
require(microbench["benchmark_top_p"] == sampling["top_p"], "microbench top-p drift")
require(microbench["benchmark_top_k"] == sampling["top_k"], "microbench top-k drift")
require(all(extended[key] == value for key, value in sampling.items()), "extended sampling drift")
require(topology["sampling"] == sampling, "topology sampling drift")
require(microbench["canonical_n"] == extended["replicates"] == 3, "canonical N mismatch")
require(microbench["variance_expansion_n"] == 10, "variance expansion N drift")

extended_protocol = ROOT / extended["substantive_audit_protocol"]
require(extended_protocol.is_file(), "missing extended substantive audit protocol")
require(
    sha256(extended_protocol) == extended["substantive_audit_protocol_sha256"],
    "extended substantive audit protocol hash drift",
)

for suite in extended["suites"]:
    task = ROOT / suite["task"]
    require(task.is_file(), f"missing task: {task}")
    require(sha256(task) == suite["current_task_sha256"], f"task hash drift: {suite['id']}")
    require(suite["max_output_tokens_cap"] == context, f"artificial output cap: {suite['id']}")
    require(all(suite[key] == value for key, value in sampling.items()), f"suite sampling drift: {suite['id']}")
    if suite.get("subject_pin"):
        subject_pin = ROOT / suite["subject_pin"]
        require(subject_pin.is_file(), f"missing subject pin: {suite['id']}")
        require(
            sha256(subject_pin) == suite["subject_pin_sha256"],
            f"subject pin hash drift: {suite['id']}",
        )
        pinned = load(subject_pin)
        pinned_shas = {
            pinned["base_sha"], pinned["head_sha"], pinned["squash_merge_sha"],
            *pinned["pr_commit_shas"],
        }
        require(
            set(suite["required_subject_shas"]).issubset(pinned_shas),
            f"required subject refs drift: {suite['id']}",
        )

fixture = next(suite for suite in extended["suites"] if suite["id"] == "dreamserver-75-pr-audit")
pr_set = Path(fixture["input_path"]) / "canonical-prs.txt"
require(sha256(pr_set) == "569b95b3384af0c4ae4b54a2c8c8f7c908b396124777927a37b5c8fa0211ecd1", "frozen PR set drift")

base = manifest["tower2"]["mmbt_base_commit"]
ancestor = subprocess.run(
    ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", base, "HEAD"],
    check=False,
).returncode
require(ancestor == 0, "campaign branch no longer descends from preregistered MMBT base")

power_rows = subprocess.check_output(
    ["nvidia-smi", "--query-gpu=power.limit", "--format=csv,noheader,nounits"],
    text=True,
).splitlines()
power_limits = [round(float(row.strip()), 2) for row in power_rows]
require(power_limits == [500.0, 500.0], f"GPU power limits are not pinned: {power_limits}")

print(json.dumps({
    "status": "valid",
    "source_revision": manifest["source_revision"],
    "model_sha256": manifest["model"]["sha256"],
    "mmproj_sha256": manifest["multimodal_projector"]["sha256"],
    "context_tokens": context,
    "sampling": sampling,
    "canonical_n": microbench["canonical_n"],
    "variance_expansion_n": microbench["variance_expansion_n"],
    "extended_suites": [suite["id"] for suite in extended["suites"]],
    "power_limits_w": power_limits,
}, indent=2))
