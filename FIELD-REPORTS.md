# Field reports

Voluntary reports from practitioners running these (or related) models on real workflows. Anecdotal but specific — meant to complement the structured benchmark data with "here's what I actually saw on my hardware on my real task." Not graded; reader-judged.

## How to contribute a report

Open a PR adding an entry to the relevant section below using the template:

```markdown
### YYYY-MM-DD — <one-line summary>

- **Model + quant**: e.g. `Qwen3.6-27B-AWQ (Cyankiwi 4-bit)` or `Qwen3.6-27B (official FP8)`
- **Hardware**: GPU(s), VRAM, key flags (e.g. `--max-model-len`, `--gpu-memory-utilization`)
- **Inference engine**: vLLM / llama.cpp / MLX / etc., version
- **Use case**: one or two sentences on what you were trying to do
- **What you observed**: the concrete behavior — failure mode, success pattern, surprising result
- **Reproducible test case** (optional): if you can share a prompt or a starter, link it. If not, omit this field.
- **Reporter**: GitHub handle or "anonymous"
```

Reports are kept as written (lightly edited for formatting only). If a maintainer adds context or a follow-up note, it goes in a `> Maintainer note:` block beneath the report so the original is preserved.

**What this is for**: surfacing patterns that don't show up in N=10 microbench cells but do show up at scale on real workflows. Examples: quant-specific behavior degradation, language-specific failures, long-horizon failure modes the bench doesn't probe.

**What this isn't**: a leaderboard, a forum, or a venue for unsubstantiated claims. Reports without specifics (model + hardware + observed behavior) are not useful and won't be merged.

---

## Reports

### Template — example entry

> This is the seed entry showing the format. Replace with real reports as they come in.

- **Model + quant**: `Qwen3.6-27B-AWQ` (Cyankiwi 4-bit AWQ)
- **Hardware**: 2× RTX PRO 6000 Blackwell, 96 GB each, 500 W cap
- **Inference engine**: vLLM 0.x.y, `--max-model-len 262144`, `--temperature 0.3`
- **Use case**: 12 task-family microbench (see [`benchmarks/microbench-phase-b-2026-05-02/`](benchmarks/microbench-phase-b-2026-05-02/))
- **What you observed**: 95.8% ship rate at N=10 across all 12 cells with `--no-think`. See `benchmarks/microbench-phase-b-2026-05-02/findings.md` for the structured writeup.
- **Reproducible test case**: see [`tooling/REPRODUCING.md`](tooling/REPRODUCING.md)
- **Reporter**: maintainer (the structured benchmark this complements)

---

## Patterns surfaced from reports

> Maintainer-curated summary of patterns that show up across multiple field reports. Updated as reports accumulate. Currently empty — will populate as reports land.

(no patterns yet — file is brand new as of 2026-05-03)

---

## Related

- Structured benchmark data: [`COMPARISON.md`](COMPARISON.md), [`SCORECARD.md`](SCORECARD.md)
- Open questions and contribution opportunities: [`ROADMAP.md`](ROADMAP.md)
- Failure-mode vocabulary: [`tooling/FAILURE-TAXONOMY.md`](tooling/FAILURE-TAXONOMY.md)
