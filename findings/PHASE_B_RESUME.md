# Phase B chain — resume guide (saved before potential power outage)

**Snapshot taken:** 2026-04-28T15:13:00Z (~11:13 EDT)
**Purpose:** Phase B = expanding the 4 differential microbench cells from N=3 → N=10 to bound 95% Wilson CIs on the headline differential claims.

## What's done as of snapshot

### Differential-cells PASS counts (after batch grading)

| Cell | 27B done / N=10 | 27B PASS | Coder done / N=10 | Coder PASS |
|---|---|---|---|---|
| p2_hallucination | 10/10 | 7 PASS | 8/10 (v9 in-flight, v10 pending) | 4 PASS |
| p3_business | 10/10 | 8 PASS (1 SIGTERM, 1 FAIL on word limit) | 3/10 (v4-v10 pending) | 3 PASS |
| p3_doc | 6/10 (v4 + v6 SIGTERM, v5 done; v7 in-flight, v8-v10 pending) | 0 PASS so far | 3/10 (v4-v10 pending) | 2 PASS |
| p3_market | 3/10 (v4-v10 pending) | 3 STRUCTURAL_PASS | 3/10 (v4-v10 pending) | 0 STRUCTURAL_FAIL |

**Total: 56 of 80 cells complete (70%).**

### Operator SIGTERMs applied (consistent with original v2/v3 doc-synthesis methodology)

All five identical-call-loops where the model wrote the same content >30 times trying to trim to a word limit:

1. `p3_doc_27b_v2` (original): 138 writes of same 775-word brief.md
2. `p3_doc_27b_v3` (original): 58 writes of same 768-word brief.md
3. `p3_business_27b_v5` (new): 49 writes of same 734-word memo.md (5 over 700 limit)
4. `p3_doc_27b_v4` (new): 35 writes of same 772-word brief.md
5. `p3_doc_27b_v6` (new): 45 writes of same 781-word brief.md

All SIGTERMs have synthetic `summary.json` written with `finish_reason: wall_killed_identical_call_loop`. Workspace tarballs extracted from containers before kill.

### In-flight at snapshot (will be lost on power-off, must re-run)

- `p2_hallucination_coder_v9` — was at iter 409/500, expected to hit stuck-detector ~30 min more wall
- `p3_doc_27b_v7` — just started, no progress yet

Both will be re-run from scratch via the chain script's idempotency check (`summary.json` doesn't exist → re-run).

## What remains after resume

| Cell | 27B remaining | Coder remaining |
|---|---|---|
| p2_hallucination | 0 (complete) | 2 (v9 + v10) |
| p3_business | 0 (complete) | 7 (v4-v10) |
| p3_doc | 4 (v7-v10) | 7 (v4-v10) |
| p3_market | 7 (v4-v10) | 7 (v4-v10) |
| **Subtotal** | **11 runs** | **23 runs** |

**Total remaining: 34 runs** (out of original 56 expansion target; chain has produced 22 new runs so far in addition to the 24 originals).

## Resume procedure (after power restore)

### Step 1 — Restart vLLM endpoints

Both vLLM containers will be killed by the power loss. Relaunch using the canonical commands from `agent-pilot/launch-commands.md`:

```bash
# 27B on GPU1 / port 8000
docker run -d --name vllm-qwen36-awq --gpus '"device=1"' --shm-size 8g \
  -v ~/models:/models:ro -p 127.0.0.1:8000:8000 \
  vllm/vllm-openai:latest \
  --model /models/cyankiwi-Qwen3.6-27B-AWQ-INT4 \
  --served-model-name qwen3.6-27b-awq \
  --host 0.0.0.0 --port 8000 --tensor-parallel-size 1 \
  --max-model-len 262144 --gpu-memory-utilization 0.92 \
  --reasoning-parser qwen3 --enable-auto-tool-choice \
  --tool-call-parser qwen3_xml

# Coder-Next on GPU0 / port 8001
docker run -d --name vllm-coder-next --gpus '"device=0"' --shm-size 8g \
  -v ~/models:/models:ro -p 127.0.0.1:8001:8000 \
  vllm/vllm-openai:latest \
  --model /models/cyankiwi-Qwen3-Coder-Next-AWQ-4bit \
  --served-model-name qwen3-coder-next-awq \
  --host 0.0.0.0 --port 8000 --tensor-parallel-size 1 \
  --max-model-len 262144 --gpu-memory-utilization 0.92 \
  --enable-auto-tool-choice --tool-call-parser qwen3_coder

# Wait for both ready
until curl -sf http://127.0.0.1:8000/v1/models >/dev/null && curl -sf http://127.0.0.1:8001/v1/models >/dev/null; do sleep 5; done
echo "both vLLM endpoints ready"
```

### Step 2 — Verify methodology comparability

Quick check that nothing drifted while powered off:

```bash
cd ~/bench
# Harness file unchanged
sha256sum agent-pilot/harness.py  # compare against v1-v3 receipt's harness sha256

# Sandbox image unchanged (still bench-sandbox:latest)
docker images bench-sandbox:latest

# Bench repo on master
git status
```

### Step 3 — Resume parallel chains

```bash
cd ~/bench

# 27B chain in background
nohup bash agent-pilot/scripts/run_diff_cells_per_model.sh 27b > /tmp/diff_27b.log 2>&1 &
echo "27B chain pid: $!"

# Coder chain in background
nohup bash agent-pilot/scripts/run_diff_cells_per_model.sh coder > /tmp/diff_coder.log 2>&1 &
echo "Coder chain pid: $!"
```

The script's idempotency check (`summary.json + workspace_final.tar.gz` exist) will skip the 56 already-done runs and continue with the 34 remaining.

### Step 4 — Operator monitoring

Watch for identical-call-loops on doc-synthesis-27B and (rarely) business-memo-27B:

```bash
# Loop signal: write_file with same content >30 times to brief.md or memo.md
python3 -c "
import json, sys
from pathlib import Path
run = sys.argv[1]
p = Path(f'agent-pilot/logs/{run}/transcript.jsonl')
paths = {}
for line in p.read_text().splitlines():
    try:
        d = json.loads(line)
        if d.get('type')=='tool' and d.get('name')=='write_file':
            paths.setdefault(d['args']['path'], []).append((d['iter'], d['args']['content'][:80]))
    except: pass
for pp, hits in paths.items():
    if len(hits) > 30:
        unique = set(h[1] for h in hits)
        if len(unique) == 1:
            print(f'LOOP: {pp} {len(hits)} writes same content')
" <run_name>
```

When a loop is confirmed (>30 same-content writes):
```bash
PID=$(ps aux | grep "harness.py <run_name>" | grep -v grep | awk '{print $2}' | head -1)
docker exec bench-sandbox-<run_name> tar -czf - -C / workspace 2>/dev/null > agent-pilot/logs/<run_name>/workspace_final.tar.gz
kill -TERM $PID
# Generate synthetic summary.json with finish_reason: wall_killed_identical_call_loop
```

(See PHASE_B_STATE_SNAPSHOT.json for the SIGTERM precedent format.)

### Step 5 — Final grading after chain completes

```bash
bash agent-pilot/scripts/batch_grade_p2.sh
bash agent-pilot/scripts/batch_grade_p3.sh
```

### Step 6 — Compute Wilson 95% CIs and update findings

```python
from statsmodels.stats.proportion import proportion_confint
# For each cell × model, 10 trials with k passes
ci_low, ci_high = proportion_confint(k, 10, alpha=0.05, method='wilson')
```

Update `findings/2026-04-28-coding-and-business-microbenches.md` and the MMBT mirror with tightened 95% CIs.

### Step 7 — Methodology audit

Re-run the v1 vs v10 receipt comparison: harness sha256, sandbox image digest, vLLM args, task SHA. All should match.

## Files preserved across power loss

- `agent-pilot/logs/p[1-3]_*/` — all completed runs' artifacts (receipt, transcript, summary, workspace tarball)
- `agent-pilot/scripts/run_diff_cells_per_model.sh` — the chain runner (parallel-friendly version)
- `findings/PHASE_B_STATE_SNAPSHOT.json` — machine-readable state at snapshot time
- `findings/PHASE_B_RESUME.md` — this document
- `findings/2026-04-28-pairwise-quality-study.md` — Phase C results (already done)
- `findings/2026-04-28-coding-and-business-microbenches.md` — Phase A + C updates (already done)

MMBT-side state (PR #10 branch `submit/aggregate-tied-finding`):
- All Phase A and Phase C work pushed to GitHub already
- Phase B substantive update is pending until chain completes

## Rollback safety

If anything's wrong after resume (vLLM doesn't start, harness file changed, etc.):
- All originals (v1-v3) committed and intact in MMBT main
- Phase A and Phase C committed and pushed to PR #10
- The 22 new v4-v10 runs already on disk — even if Phase B never completes, we have partial N=10 data we can write up as "in progress" findings
