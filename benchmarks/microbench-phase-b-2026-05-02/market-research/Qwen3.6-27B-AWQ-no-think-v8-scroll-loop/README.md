# p3_market 27B-no-think v8 — `scroll-loop` (operator-SIGTERM)

> Second instance of the [`scroll-loop`](../Qwen3.6-27B-AWQ-no-think-v1-scroll-loop/) pathology in 10 runs of `p3_market` 27B-no-think — confirms the pattern is reproducible, not a one-off.

## What happened

Started 2026-05-02 17:53 UTC. Ran for ~75 minutes producing partial research (1Password / Bitwarden / Dashlane sections written) before stalling on LastPass pricing — same downstream task as v1. From iter 86 onward, the model emitted the same digit-stripped bash template for **31 consecutive iterations** before operator-SIGTERM at iter 116.

This run was caught much earlier than v1 (31-iter streak vs 155). Substance-monitoring detection logic now flagged the streak at exactly the documented `>30 same-content writes` threshold.

The bash template was structurally identical to v1's PCMag-scrape pattern, except this time the model varied the *output filename* (`/tmp/lastpass-business-pcmag${N}.html`) per iter as well as the slice offset — same root failure mode (walking a JS-rendered page in fixed slices), slightly different surface form.

## Why this matters

Two scroll-loops of the same shape on the same task in the same N=10 sample = **20% scroll-loop rate for 27B-no-think on `p3_market`**. Combined with the [`runaway-generation`](../Qwen3.6-27B-AWQ-no-think-v5-runaway-generation/) on v5 (10%), the cell has a 30% pathological rate even excluding the harness's natural stuck-detector signal.

The actionable read: **scroll-loops are an operationally distinct failure class from the `wall_killed_identical_call_loop` runs** that the harness catches via its 500-no-progress guard. Both `p3_business` and `p3_doc` had 2/10 wall_killed runs at N=10, and those likely follow the same scroll-loop pattern (full transcripts not yet hand-audited). The difference here is timing: the scroll-loop sub-label catches the pattern at ~iter 30 of the streak rather than at iter 500 of no-progress.

## What's published here

Metadata files only:
- `cost.json` — 76 min wall, $0.026 upper-bound (capped early via SIGTERM; would have run another ~25 min to harness threshold)
- `label.json` — primary `identical-call-loop`, captures the iter range and operator-SIGTERM context
- `receipt.json` — task SHA, harness SHA, model + flags
- *(no `summary.json` — operator-SIGTERM bypassed teardown)*

Full transcript in source bench's `submit/phase-b-overnight-2026-05-02` branch at `agent-pilot/logs/p3_market_27b-nothink_v8/transcript.jsonl`.

## Cross-references

- [`../Qwen3.6-27B-AWQ-no-think-v1-scroll-loop/`](../Qwen3.6-27B-AWQ-no-think-v1-scroll-loop/) — first scroll-loop instance, with the canonical iters 198 vs 207 excerpt
- [`../../findings.md`](../../findings.md) § "Two new pathologies surfaced"
- [`../../../../tooling/FAILURE-TAXONOMY.md`](../../../../tooling/FAILURE-TAXONOMY.md) § `scroll-loop` sub-label
