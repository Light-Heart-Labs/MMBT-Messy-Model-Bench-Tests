# market-research

> Agent is asked to evaluate enterprise password managers for a 50-seat team and produce a recommendation. Concrete deliverables required: `recommendation.md` (specific product + tier + pricing math), `comparison.md` (5 named competitors evaluated on a fixed dimension list), `sources.md` (citations to publicly-accessible URLs).
>
> **Pass criteria** (structural): all required files exist, recommendation has named product / tier / pricing / 50-seat math, comparison has all 5 competitors, sources has inline citations. *Citation validity is a hand-grading placeholder.*

## Why this task

This is the cleanest test of an agent's ability to drive a multi-step internet-research workflow available in the suite. It demands sustained tool-use loops (fetching pages, extracting data, cross-referencing), structured output organization (separate files for separate concerns), and concrete decision-making (not vague tradeoff narratives — a specific product, a specific tier, with the math).

The expectation walking into this benchmark was that **both** local 30B-class quantized models would fail — internet research demands sustained work that smaller models tend to break on. That expectation turned out to be wrong for 27B and right for Coder-Next.

## Results — N=3 per model

| Model | PASS | Files produced | Products evaluated | Inline cites | Distinct URLs | Wall (median) |
|---|---|---|---|---|---|---|
| **[Qwen3.6-27B-AWQ](Qwen3.6-27B-AWQ/)** | **3/3 STRUCTURAL_PASS** | recommendation.md + comparison.md + sources.md (all 3 runs) | 5/5 (1Password, Bitwarden, Dashlane, Keeper, LastPass) every run | 12-18 per run | 29-33 per run | 18.9 min |
| **[Qwen3-Coder-Next-AWQ](Qwen3-Coder-Next-AWQ/)** | **0/3 STRUCTURAL_FAIL** | none of the 3 runs produced the required files | n/a | n/a | n/a | 19.1 min (incl. stuck) |

Coder-Next failure modes across N=3:
- v1: stuck-in-research (read sources without writing structured output)
- v2: stuck-in-research (same)
- v3: vLLM api_error (probably context overflow at 65 iters)

This is the **second-largest local-model superiority signal in the entire benchmark suite**, behind only the adversarial-hallucination cell. The earlier expectation that both models would fail at this task class was based on the prior dreamserver-PR-audit data; on this smaller-scoped task with cleaner deliverable shape, 27B drives the workflow and Coder-Next doesn't.

## What "STRUCTURAL_PASS" does and doesn't claim

STRUCTURAL_PASS asserts: required files exist, recommendation has the right shape (named product, tier, pricing, 50-seat math), comparison has all 5 competitors, sources has inline cites with distinct URLs.

STRUCTURAL_PASS does NOT assert: the cited URLs actually exist; the URLs say what they're cited for; the pricing numbers are accurate as of the run date; the product features attributed to each competitor are correct. These are the **hand-grading placeholders** in `grade.json`:

```json
"_HAND_VERIFICATION_REQUIRED_": "structural pass is necessary but not sufficient. The fabrication-and-citation-validity dimensions need human verification of each cited source.",
```

For a downstream consumer relying on this output, sample-grade the citations rather than consuming blind. The structural gap between the models is the strongest claim this entry supports right now.

## Cross-references

- [`../findings.md`](../findings.md) § "Market research splits the models hard — 27B drives the workflow, Coder-Next can't"
- [`../../../SCORECARD.md`](../../../SCORECARD.md) § microbench-2026-04-28 (market-research row + ★ note)
- [`../../../tooling/FAILURE-TAXONOMY.md`](../../../tooling/FAILURE-TAXONOMY.md) § stuck-in-research, api-error

## Task starter

This task does NOT have a planted-fact ground-truth file (unlike most of the other Phase 3 tasks) — it's an open-ended internet-research task graded against a structural rubric in `agent-pilot/graders/ground_truth/phase3_market_research_rubric.json`. The agent gets an unrestricted internet bash sandbox and is told what shape of output to produce. There is no leakage risk because the rubric defines pass criteria abstractly (e.g., "5 distinct products evaluated") without the answer.
