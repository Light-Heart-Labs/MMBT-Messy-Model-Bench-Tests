# Harness changelog

A short log of harness changes and the bugs that prompted them. Live mainly to explain *why* the harness has its current shape, since runs that exposed each bug have been pruned from the results namespace (they were harness-faulted, not capability data).

Each fix is in the git history if you want to inspect the diff.

## 2026-04-27

### `--require-files` and `--require-git-tag` (strict-done validation)

Added in response to the MMBT feedback round on the Qwen3.6-27B-AWQ N=1 entries: across three runs at temp=0.3, the model produced excellent analytical content but never shipped `verdict.md`, never tagged a release, never called `done()`. Open question: is that a *model* failure (27B can't follow the spec under pressure) or a *scaffold* failure (the harness's `done` tool is too lenient — the model thinks it's done because nothing tells it otherwise)?

`--require-files <name1,name2,...>` and `--require-git-tag` are the harness-equivalence test. When set, the `done` tool runs validation before accepting:

- Each required filename is matched via `find /workspace -maxdepth 3 -name <name> -type f` so the agent's choice of audit-repo location (e.g. `/workspace/audit-pr-1057/` vs `/workspace/audit-repo/` vs `/workspace/`) doesn't matter.
- `--require-git-tag` looks for any `.git` directory under `/workspace` at depth ≤ 2 with at least one annotated tag.

If any requirement is missing when `done()` is called, the call is rejected with a tool-error: `DONE_REJECTED: Required artifacts missing — task spec demands these before completion: <list>. Continue working — produce these (or update existing files to match the requirements) before calling done() again.` The loop continues; the model can produce the missing files and retry.

Receipt's `sandbox.runtime` now records `require_files` and `require_git_tag` so strict runs are distinguishable from baseline.

This is an opt-in flag — default behavior unchanged for existing runs.

### `--stuck-threshold` flag (was hardcoded 30)

The temp-fix smoke (`coder_pr_audit_smoke_v2`) cleared the deterministic loop trap and let Coder-Next do real work — it fetched 66 PR branches, init'd the audit-repo, made a real first commit, recorded the baseline SHA — then died at iter 54 because of **30 consecutive `ls -la` operations** exploring DreamServer's directory tree. None of those changed the workspace, so the stuck-detector fired even though the agent was doing legitimate codebase recon.

The threshold of 30 was tuned for the memo/board/code-adoption tasks where the entire job fits in ~100 iters (Coder-Next averaged 95 iters on the memo). At that scale, 30 iters of no-write is a strong loop signal. For a 75-PR audit where the agent reasonably needs 50+ ls/cat/git operations to understand the codebase before producing per-PR verdicts, 30 is wrong — it punishes recon, not loops.

`--stuck-threshold` is now configurable per-run, default 30 (preserves prior behavior; receipts under the new harness SHA reflect the actual value used). Suggested 80-150 for long-horizon tasks. Genuine loops still die within `(threshold × ~1.5 s)` of starting, so the cost of a higher threshold is bounded.

Receipt's `harness_loop_config.stuck_threshold_iters` is now dynamic. Also renamed `max_iters_default` → `max_iters` since it now reflects the actual passed-through value, not the default.

### `--temperature` flag (was hardcoded 0.0)

Added in response to the first DreamServer PR-audit smoke run (`coder_pr_audit_smoke_v1`), where Coder-Next did 11 iters of real work (cloned the repo, listed PRs, gathered file lists for ~10 PRs) and then **fell into a deterministic fixed-point loop**: 30 consecutive iterations of the same `curl .../pull/1057/files` call with no workspace change, until the stuck-detector fired at iter 41 (112 s wall).

Root cause: `temperature: 0.0` + `seed: 42` makes the agent fully deterministic. When a tool call's output doesn't move the conversation forward in the model's view, the next response is identical, the next tool call is identical, the next result is identical — forever, until something else perturbs state. The stuck-detector kills the run, but no useful work happens after the loop entered.

The harness changelog already noted "Determinism is approximate" because of vLLM's bf16 path non-determinism, so we never had bitwise reproducibility anyway — we were keeping seed=42 + temp=0 for a property we didn't actually have, while paying a real cost in loop traps on long-horizon tasks.

`--temperature` is now configurable per-run, default 0.0 (preserves prior runs' settings; receipts under the new harness SHA will reflect the actual value used). For agentic long-horizon tasks: 0.3–0.5 breaks the trap without much off-task drift. `seed: 42` is still sent on every request — it's harmless at temp>0 and gives a reproducibility prior for replays.

The receipt's `inference_request_defaults.temperature` is now dynamic (was hardcoded 0.0). Past receipts are unaffected.

### Sandbox capability flags: `--gh-token`, `--docker-socket`, `--gpus`

Added in preparation for the DreamServer PR-audit task (`task_dreamserver_pr_audit.md`), which requires the agent to (a) auth against api.github.com to read 75 PRs without hitting the 60 req/hr unauth ceiling, (b) run the DreamServer installer inside clean sibling containers, and (c) optionally exercise GPU code paths on real hardware.

- `--gh-token` accepts a literal token, `@env` (read $GH_TOKEN/$GITHUB_TOKEN from the caller), or `@gh` (call `gh auth token` on the host). Resolved value is exported as both `GH_TOKEN` and `GITHUB_TOKEN` in the sandbox. **The token value is never written to receipt.json** — only `gh_token_set: bool`.
- `--docker-socket` bind-mounts `/var/run/docker.sock`. The sandbox image now ships with `docker.io` so the agent has a CLI on the path. Caveat: this gives the sandbox root-equivalent access to the host docker daemon — fine for local benchmarking, not fine for adversarial tasks.
- `--gpus` is a pass-through to `docker run --gpus`. Note that on Tower2 the sandbox shares GPUs with the vLLM container hosting the model under test, so heavy in-sandbox CUDA work will contend with inference latency.

Sandbox image gained two new packages: `docker.io` (debian default) and `gh` (official cli.github.com apt repo). Build the image once with `docker build -t bench-sandbox:latest agent-pilot/` after pulling these changes.

Receipts now include `sandbox.runtime: {gh_token_set, docker_socket, gpus, input_mount}` so reproducibility from receipt alone still holds for runs that used these flags.

## 2026-04-26

### Receipts + canonical launch commands

`a1d59fb` — `record_environment()` writes `logs/<run>/receipt.json` before the agent loop starts. Captures: vLLM container `Args` (the exact launch flags), image digest + container ID + start time, sandbox image id, harness git SHA + dirty flag + file sha256, task file sha256 + size, host kernel/OS, full nvidia-smi snapshot at run start, and the inference request defaults the loop will use. Pairs with `agent-pilot/launch-commands.md` which documents the canonical `docker run` form for each model.

Goal: any past run is reproducible from its receipt alone — checkout the harness SHA, rebuild the sandbox image from that SHA, launch vLLM with the captured args, point the harness at it.

### urlopen timeout: 900 s → 3600 s

`3557ee7` — A 27B-AWQ run on the investment-memo task was cut short by `urllib.request.urlopen(req, timeout=900)`. The model was actively making progress (last 5 tool calls were fresh python scripts attempting different data sources, stuck-detector at 1/30) but a single inference call exceeded 900 s — almost certainly because thinking-mode models can spend many seconds reasoning between tool calls.

900 s was wrong for thinking models on hard tasks. Bumped to 3600 s. The stuck detector (workspace state hash, kills after 30 iters of no change) remains the primary terminator for genuine model stalls; the urlopen timeout is now just a backstop for hung connections, which was its original intent.

### Dynamic `max_tokens`

Same era — replaced the fixed `max_tokens: 200000` per request with `min(64000, max_model_len - last_prompt_tokens - 14000)`. The original 200K was eating all the context budget so as conversation history grew vLLM would 400 with "input is too long". Dynamic computation leaves prompt headroom that scales with iteration count.

### `docker_exec`: argv → stdin

`c60acfe` — A Coder-Next run died with `OSError: [Errno 7] Argument list too long` at iter 38 when the model emitted a ~680-token bash heredoc as a single tool call. Linux's argv+envp limit is ~128 KB and `docker exec ... bash -c "<long>"` puts the entire command on argv.

Switched to `docker exec -i ... bash -s` with the command piped on stdin. No argv constraint, same workdir/timeout semantics. Sanity-checked with a 200 KB synthetic command (rc=0).

This bug had been silently affecting Coder-Next runs all along — Coder-Next is biased toward emitting big bash heredoc tool calls vs the more modular tool calls a thinking-mode model tends to make. Score on the same model+task swung ~4× once fixed (score was a harness ceiling, not a model ceiling). **Worth checking any harness-mediated agent before scoring it.**

## Methodology lessons baked in

1. **Receipts are mandatory.** Every run writes one before the loop starts. Reproducible-from-receipt is the bar.
2. **Argv-length is a real harness constraint.** Long tool calls must go via stdin.
3. **Determinism is approximate.** Same model, same prompt, `temperature=0` — different runs can pick different companies and reach different states. vLLM's bf16 paths aren't bitwise-deterministic across runs (cuBLAS workspace + batch reordering effects). Plan for N≥3 per (model × task) when moving from pilot to formal eval.
4. **Stuck detector is the primary terminator.** Workspace-state hash; if no file/commit changes for 30 consecutive iters, kill. Held up cleanly across all observed runs — never falsely fired during real progress, always fired on actual stalls.
