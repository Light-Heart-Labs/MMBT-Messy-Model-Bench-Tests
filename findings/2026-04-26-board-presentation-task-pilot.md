# 2026-04-26 — Board-presentation task pilot (Coder-Next vs 27B-AWQ)

> Second task type: take the GTLB investment-memo canonical deliverable, build a board-of-advisors presentation with auditable traces. Both models completed; very different style profiles.

## Setup

- **Task**: `agent-pilot/task_board_presentation.md` — build a 15-25 slide deck from `/input/repo/` (mounted read-only), with every claim traced to a specific commit/file/line in the input
- **Input mount**: `agent-pilot/inputs/27b-awq-gtlb-memo/` (extracted from `27b_invest_memo_v2` tarball, .git intact, 3-commit history)
- **vLLM image**: `vllm/vllm-openai:latest` (`sha256:2622f38a…`) for both
- **Sandbox**: `bench-sandbox:latest` rebuilt with `python-pptx`, `matplotlib`, `plotly`, `kaleido`, `Pillow`, `graphviz` + cairo/pango/font runtime libs
- **Harness git SHA at run**: `56abc1c` (with `--input-mount` and per-run sandbox)
- Both runs at `temperature=0`, no system prompt, full task text verbatim

## Results

| metric | Coder-Next | 27B-AWQ |
|---|---|---|
| **finish_reason** | `done_signal` | `done_signal` |
| Iterations | 87 | 66 |
| Wall time | 10.6 min | 34 min |
| Total completion tokens | 42,133 | 45,208 |
| **Slide count** | 14 (below 15-25 spec) | **16** (in spec) |
| **PPTX file size** | 43 KB | **922 KB** (21× larger; chart embedding) |
| **Charts** | 3 (financial trajectory, scenario, competitive) | **7** (revenue/margins, ARR/NRR, competitive, scenario distribution, risk heatmap, reasoning trail, confidence spectrum) |
| Trace files | 8 (single-source) | 5 (**multi-source cross-check**) |
| Reconciliation entries | 5 | 5 |
| Reconciliation depth | claim → source value | **claim → raw → conversion → rounding → cross-check** |
| Dead-ends entries | 4 substantive | 7 substantive (incl. honest "agent cannot do X" admissions) |
| ADRs | 2 (slide-structure, chart-design) | 2 (color-palette, chart-conventions) |
| **Commits** | **16** (granular, frequent) | 4 (chunky: initial, storyboard, complete, verify-reproducibility) |
| Storyboard committed before deck | ✓ (ea155c8 → e7f6ca5) | ✓ (832ccb3 → dc52823) |
| Total files | 42 | 56 |

Both met the explicit task requirement of "every required slide topic present" and "storyboard committed before any slide". Both have a `v1.0.0` release tag.

## Spot-checks (performed during audit)

### Coder-Next
- **Trace claim "price target $42 at line 10 of memo"**: verified — actual line 10 of `gitlab_investment_memo.md` is `**12-Month Price Target:** $42.00 (95% upside)` ✓
- **Reconciliation claim "Revenue $955M from income_statement_annual.csv row Total Revenue col 2026-01-31"**: verified — actual CSV value is `955224000.0` ✓
- **Chart regeneration**: ran `scenario_analysis.py`, produced identical PNG ✓

### 27B-AWQ
- **Trace `trace_01_current_price.md`**: claims 3 cross-confirming sources (extracted/company_info.json + memo + analysis_summary). All three exist with the value `21.51` ✓
- **Reconciliation #1**: shows full chain raw `955224000.0` → / 1M → `955.2M` → rounded → `$955M`, plus 2 cross-checks. ✓ — more thorough than Coder-Next's reconciliation
- **Dead-ends entry "Customer Case Studies — rejected because no customer data is available in the input repo. Including fabricated case studies would violate the auditability requirement."** — honest acknowledgment of agent limitations

## Stylistic differences

**Coder-Next is the production engineer.** Granular commits (16 vs 4), faster (10.6 min vs 34 min), tighter audit files. Made fewer charts but each one in a clean reproducible script. Skipped the deeper multi-source verification.

**27B-AWQ is the deliberate analyst.** Few large commits (4 vs 16), much slower (34 min), but each chart is data-rich (922KB PPTX implies real embedded visualizations), traces cross-check across 3 sources, dead-ends include explicit "the agent cannot do X" admissions. The deck itself is substantively bigger.

Neither is "better" in an absolute sense — they're different operating points on a quality-vs-speed-vs-process tradeoff:
- Coder-Next wins on commit hygiene and time efficiency
- 27B-AWQ wins on depth-per-artifact and content richness
- Both meet the auditability bar

## Rough rubric scoring

| dimension | Coder-Next | 27B-AWQ |
|---|---|---|
| Repo structure | 95 | 95 |
| Storyboard before slides | 100 | 100 |
| Deck content (topics covered) | 90 | 95 |
| Slide count in spec | 90 (14, below) | 100 (16) |
| Chart richness | 70 (3 charts) | 95 (7 charts) |
| Charts reproducible | 95 | 95 |
| Trace files | 90 (8 files, single-source) | 95 (5 files, multi-source) |
| Reconciliation depth | 80 | 95 |
| Dead-ends substance | 75 | 90 |
| Commit hygiene | 95 (16 substantive) | 60 (4 chunky) |
| Wall efficiency | 95 (10 min) | 70 (34 min) |
| **Overall (rough)** | **~88/100** | **~92/100** |

## Observations against the memo-task results

Recall the memo task: 27B ~85, Coder-Next ~80 (best runs). On the deck task with same models: 27B ~92, Coder-Next ~88. **Both models scored higher on the deck task** than on the memo task. Hypotheses for why:

1. **Tighter input bounds**: the deck task's input is a fixed repo, not "go find any company". Eliminates the search-the-world variance source.
2. **Code-heavy task structure**: building a deck is mostly Python (chart scripts, PPTX generation). Plays to Coder-Next's strengths in particular.
3. **The memo-task deliverable provided structured input**: when an agent's output becomes the input for another agent, the second agent has cleaner data than what the first one had to gather.

This last point is interesting — the agent pipeline behavior may be net additive: agent_2 picks up where agent_1 left off rather than starting fresh.

## Open questions

- **Variance**: this is N=1 per model on a new task. We documented in the prior batch that N=1 is unsafe; same caveat applies here. Both models could land very differently on a second run.
- **Cross-input variance**: would the same models do similarly well building a deck from the Coder-Next DocuSign memo (which has different content depth, PT-vs-DCF inconsistency, etc.)? Different input quality might surface different agent behaviors.
- **Quality of the actual deck content**: I spot-checked traces and reconciliation but didn't open the .pptx files and read the slide text. A deeper audit would compare narrative quality, prose, and whether the "thesis in the agent's own words" actually quotes the memo accurately.

## Artifacts

Per-run:
- `agent-pilot/logs/coder_board_pres_v1/{receipt,summary,transcript}.json[l]` + `workspace_final.tar.gz`
- `agent-pilot/logs/27b_board_pres_v1/...` (same)

Canonical deliverables (full repos with `_agent_git_history` preserved):
- `agent-pilot/canonical-deliverables/coder-next-board-deck-gtlb/`
- `agent-pilot/canonical-deliverables/27b-awq-board-deck-gtlb/`

Inputs (immutable, mounted read-only at run time):
- `agent-pilot/inputs/27b-awq-gtlb-memo/` (the GTLB investment memo, with .git intact)
