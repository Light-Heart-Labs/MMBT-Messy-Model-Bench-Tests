# Graders v2 — changes vs v1

Preregistered fixes (PREREGISTRATION.md section 8) for the three grader/fixture
defects documented in the study's defect report (D1/D2/D3). The v1 graders,
every existing `grade.json`, receipts and prior campaign logs are untouched;
the prior corpus remains exploratory evidence graded by v1. v2 is the grading
contract for the corrective campaign only.

## Provenance (v1 sources, sha256 at copy time)

| v2 file | copied from | v1 sha256 |
| --- | --- | --- |
| `phase3_business_memo_grade.py` | `tooling/graders/phase3_business_memo_grade.py` | `691c5c6cec0f3bbf2fc86e80c47dd3fc2bde4873dc630297a0aea13edd548d7b` |
| `phase3_doc_synthesis_grade.py` | `tooling/graders/phase3_doc_synthesis_grade.py` | `8c117c0a3bfec94a91f94e49bb5b4281a458bcc4a650e9ae86e2450f0f5cac0a` |
| `phase3_writing_editing_grade.py` | `tooling/graders/phase3_writing_editing_grade.py` | `a3461f31be9d24cc1c5132fff4bff96a27af77af2457dad839ef5498afba8f56` |
| `phase3_project_mgmt_grade.py` | `tooling/graders/phase3_project_mgmt_grade.py` | `e1c3a9190e6d19cffd76734c8c922450b22d674bd5fd2db052fef31f91777bca` |
| `phase2_triage_grade.py` | `tooling/graders/phase2_triage_grade.py` | `ea3eebcf6a2fc085276e555f2cb1a54239e1dc9286bac3cb2300f01929b855a1` |
| `ground_truth/phase2_triage.json` | `tooling/graders/ground_truth/phase2_triage.json` | `6ca3763f32abfe3a5b8dfa56662c9083f91f81c2c3d06d3117bfb974367669d1` |

v2 task briefs (copies, `tooling/tasks/v2/`) derive from the v1 briefs:
`task_doc_synthesis.md` (`acce4828…`), `task_business_memo.md` (`71f459a8…`),
`task_writing_editing.md` (`8932f7c1…`), `task_project_mgmt.md` (`405ec07e…`),
`task_triage.md` (`d92feeb8…`).

## D1 — word-counter contract

The four length-gated phase-3 graders (`p3_business`, `p3_doc`, `p3_writing`,
`p3_pm`) replaced the v1 regex counter `len(re.findall(r"\b\w+\b", text))` with
a subprocess call to `wc -w` under `LC_ALL=C.UTF-8` (the harness container
locale, verified), via the shared `wordcount_v2.py`. A ±3% tolerance band
applies at each ceiling: pass iff `wc -w count <= floor(ceiling * 1.03)`
(700 → 721; per-audience 250 → 257, 350 → 360, 400 → 412).

The matching v2 briefs state the counter and the band explicitly, so model and
grader now share one contract. `p3_market` computes a word count but never
gates on it; it is unaffected and has no v2 copy. Deliberate disclosure in the
`task_project_mgmt.md` v2 brief: the v1 brief said "aim for ≤500 words" while
the grader gated at 700; the v2 brief now names the 700-word graded ceiling —
stating the real gate was judged less distorting than gating on an unstated
number.

## D2 — `p3_pm` semantic R3

`phase3_project_mgmt_grade.py` v2 re-checks a literal-keyword miss on risk R3
(legal / private-beta contract delay) against the semantic pattern adopted
verbatim from the repository's existing correction module
`tooling/correct_gemma4_project_mgmt_grades.py` `RULES["R3"]["patterns"][0]`
(sha256 `86eeec68b6c7114fb0672566220938e35fa605cd1b89ac4b0863f7cfe305f581`),
applied to the same normalized text. A semantic match is recorded as
`"keyword": "r3-semantic-equivalent-v2"` plus a `semantic_rules` block in the
grade. Only R3 is upgraded: it is the only rule with a decisive natural
experiment (`p3_pm_qwen36-nothink-card_v2`/`_v8` vs `_v4` — byte-identical risk
rows except the contraction `hasn't`/`has not` deciding PASS vs FAIL). The
upstream R2 replacement fires on 64/64 prior-corpus cells, which is a rubric
rewrite, not a false-negative fix, so R2/D3_mobile/D4_option_b stay literal.

## D3 — `p2_triage` brief/ground-truth alignment

Two contradictions, both resolved toward the brief (a model must not be scored
down for obeying the written instructions):

1. The brief defines urgency `n/a` as "for noise/spam where urgency doesn't
   apply"; the v1 ground truth labeled the three spam tickets 004/009/021
   `low` and contained zero `n/a` labels. 64/64 prior-corpus cells answered
   `n/a`. The v2 ground truth labels 004/009/021 `n/a`.
2. Ticket 029 (extortion): the brief's rules-of-the-road names "extortion
   threats" as `spam-or-noise`, while its `security-incident` gloss listed
   "extortion" and the v1 ground truth said `security-incident`/`urgent`
   (64/64 cells followed the rules-of-the-road). Resolved per preregistration
   to the rules-of-the-road reading: v2 ground truth says
   `spam-or-noise`/`n/a`, and the v2 brief removes "extortion" from the
   `security-incident` gloss (adding "extortion/threat emails with no
   substantive product content" to the `spam-or-noise` gloss) so brief and
   ground truth agree. The substantive alternative reading — an extortion
   email claiming customer data is a security incident — is acknowledged here
   and in the ground-truth notes; it is a defensible rubric, but not the one
   the models were instructed with, and consistency wins for the corrective
   study.

The v2 grader parses the closed urgency vocabulary from the v2 brief's
`## Urgency` section and validates both sides against it: an
out-of-vocabulary ground-truth label aborts grading (fixture defect — exactly
what D3 was), and an out-of-vocabulary agent label is an urgency error
reported in `errors.invalid_urgency_labels`. The brief path and sha256 and the
ground-truth sha256 are recorded in every grade for the evidence manifest.

## Tests

`tests/` covers all three fixes; run either way:

    python3 -m pytest tooling/graders/v2/tests -q
    python3 tooling/graders/v2/tests/test_<name>.py

All code is python3-stdlib-only (plus `wc` from coreutils, which is the point).
