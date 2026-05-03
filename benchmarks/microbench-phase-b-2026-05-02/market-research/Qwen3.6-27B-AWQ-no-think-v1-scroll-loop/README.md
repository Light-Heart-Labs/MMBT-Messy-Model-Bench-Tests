# p3_market 27B-no-think v1 — `scroll-loop` (operator-SIGTERM)

> Single-run failure-mode entry. The new `scroll-loop` sub-label of `identical-call-loop` was added to [`tooling/FAILURE-TAXONOMY.md`](../../../../tooling/FAILURE-TAXONOMY.md) because of this exact run — it's the canonical example.

## What the task asked for

Evaluate 5 password-manager products (1Password, Bitwarden, LastPass, Dashlane, Keeper) against pricing / security / SSO / CLI criteria, hitting live vendor pricing pages over the network, and produce a recommendation memo with citations. See [`tooling/tasks/task_market_research.md`](../../../../tooling/tasks/task_market_research.md).

## What happened

Started 2026-05-02 16:35 UTC. Ran for 2 hours producing real research (1Password / Bitwarden / Dashlane / Keeper sections all written) before getting stuck on LastPass pricing. From iter 74 onward, the model emitted **the same 758-character bash command for 155 consecutive iterations**, differing only by the Python slice offset.

The model was walking PCMag's `best-password-manager-for-business` HTML response in 20,000-byte windows looking for LastPass pricing it couldn't find. Operator-SIGTERM at iter 228 (155-iter streak detected via the documented `>30 same-content writes` methodology rule).

## The two iterations side-by-side

```bash
# iter 198 (excerpt — 758 chars total):
curl -sL "https://www.pcmag.com/picks/best-password-manager-for-business" | python3 -c "
import sys, re, html as h
content = sys.stdin.read()
content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
# ... HTML strip ...
print(content[2615000:2635000])
"

# iter 207 (same 758 chars, only the slice offset differs):
curl -sL "https://www.pcmag.com/picks/best-password-manager-for-business" | python3 -c "
# ... identical setup ...
print(content[2795000:2815000])
"
```

Each iter incremented the slice offset by +20,000 chars. By iter 228 the model had walked ~3 MB of HTML in 20K-byte windows looking for a pricing table that wasn't in the rendered HTML at all (LastPass uses JS-loaded pricing — invisible to a curl scrape).

## Why the harness didn't catch it

The harness has two stuck guards:

1. **Content-hash same-content guard** — fires after 30+ identical *raw* tool-call hashes. Did NOT fire here because the offsets differ across iters; raw hashes are all unique.
2. **Workspace-hash stuck-threshold (500 iters)** — fires after 500 unchanged-workspace iters. Was at **205/500 at iter 207** when operator killed. Would have fired in another ~295 iters (~50 more minutes).

The harness's same-content guard is hash-equality-based. The fix in operator monitoring: **digit-strip** tool-call commands before comparing. Iters 74-228 all collapse to *one* unique digit-stripped template. Tail-streak ≥ 30 identical templates triggers SIGTERM.

## What this means for decisions

`p3_market` is a known trap for 27B-no-think — 30% pathological rate at N=10 across three distinct mechanisms (this scroll-loop, [v8](../Qwen3.6-27B-AWQ-no-think-v8-scroll-loop/) scroll-loop, [v5](../Qwen3.6-27B-AWQ-no-think-v5-runaway-generation/) runaway-generation). Without operator monitoring, each scroll-loop costs an additional ~50 minutes of GPU time waiting for the harness's 500-iter threshold to fire. With monitoring, the loop is caught at ~iter 30 of the streak and SIGTERM'd within ~5 minutes.

## What's published here

The published metadata files are:
- `cost.json` — wall time and upper-bound $ estimate (run was 119 min before kill, $0.041)
- `label.json` — primary `identical-call-loop`, with the operator-monitoring narrative in `notes`
- `receipt.json` — task SHA, harness SHA, model + flags
- *(no `summary.json` because operator-SIGTERM bypassed harness teardown)*
- *(no `workspace_final.tar.gz` for the same reason; partial artifacts exist in the source bench's submit branch)*

Full transcript (228 iters, ~290 KB) is preserved in the source bench's `submit/phase-b-overnight-2026-05-02` branch at `agent-pilot/logs/p3_market_27b-nothink_v1/transcript.jsonl`.

## Cross-references

- [`../../findings.md`](../../findings.md) § "Two new pathologies surfaced" — discussion in context with `runaway-generation`
- [`../../../../tooling/FAILURE-TAXONOMY.md`](../../../../tooling/FAILURE-TAXONOMY.md) § `scroll-loop` sub-label — the formal taxonomy entry this run defined
