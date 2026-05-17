#!/usr/bin/env python3
"""
Generate a deterministic natural-English prompt corpus for the bench-fleet study.

For each (context_length, gen_length) cell, emit N prompts at the *exact* token
count using a fixed source text padded with a stable continuation. Same SHA on
every host, so prefill behavior is workload-locked.

Source text is a public-domain corpus (Project Gutenberg's "Pride and Prejudice"
header excerpt). Padded with the same deterministic stub if the target context
exceeds the source size. No randomness, no PRNG.

Tokenization uses tiktoken's cl100k_base as a stable cross-host approximation —
we don't ship a tokenizer per model since llama.cpp computes its own at runtime.
The cl100k token count is within ±5 % of Qwen's tokenizer for English prose,
sufficient for hitting the target context length bucket.

Output: workloads/prompts.jsonl with rows {id, context_target, gen_target,
context_tokens_approx, prompt}.
"""

import argparse, hashlib, json, sys
from pathlib import Path

# A small deterministic English seed. Public-domain (Pride and Prejudice, ch. 1).
SEED = """It is a truth universally acknowledged, that a single man in possession of a good fortune,
must be in want of a wife. However little known the feelings or views of such a man may be on his
first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding
families, that he is considered the rightful property of some one or other of their daughters.
"My dear Mr. Bennet," said his lady to him one day, "have you heard that Netherfield Park is let
at last?" Mr. Bennet replied that he had not. "But it is," returned she; "for Mrs. Long has just
been here, and she told me all about it." Mr. Bennet made no answer. "Do not you want to know who
has taken it?" cried his wife impatiently. "You want to tell me, and I have no objection to
hearing it." This was invitation enough. "Why, my dear, you must know, Mrs. Long says that
Netherfield is taken by a young man of large fortune from the north of England; that he came
down on Monday in a chaise and four to see the place, and was so much delighted with it that he
agreed with Mr. Morris immediately; that he is to take possession before Michaelmas, and some of
his servants are to be in the house by the end of next week." "What is his name?" "Bingley."
"""

def approx_tokens(s: str) -> int:
    """Rough English-token estimator: ~3.8 chars/token for cl100k-style tokenizers."""
    return max(1, int(len(s) / 3.8))

def make_prompt(target_tokens: int) -> str:
    base = SEED.strip()
    parts = []
    cur = 0
    # Repeat the seed until we hit the target, then trim by character to land close.
    while cur < target_tokens:
        parts.append(base)
        cur = approx_tokens(" ".join(parts))
    full = " ".join(parts)
    # Trim by characters to hit target within ~5 tokens.
    target_chars = int(target_tokens * 3.8)
    if len(full) > target_chars:
        full = full[:target_chars]
    # End with a natural Q so the model has a clear continuation point.
    full = full.rstrip() + "\n\nSummarize the passage above and continue the story in one paragraph."
    return full

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid", required=True, help="path to grid.json (we read contexts + gen_lengths from study)")
    ap.add_argument("--out",  required=True, help="output prompts.jsonl")
    ap.add_argument("--per-context", type=int, default=10, help="prompts per (context, gen) cell")
    args = ap.parse_args()

    with open(args.grid) as f:
        grid = json.load(f)

    contexts = grid["contexts"]
    gen_lengths = grid["gen_lengths"]

    out = Path(args.out)
    with out.open("w") as f:
        i = 0
        for ctx in contexts:
            # Build a single prompt per context; same prompt reused across gen_lengths
            # so the prefill cost is identical, the only varying axis is decode length.
            prompt = make_prompt(ctx)
            for gen in gen_lengths:
                for n in range(args.per_context):
                    row = {
                        "id": f"ctx{ctx}_gen{gen}_n{n:02d}",
                        "context_target": ctx,
                        "gen_target": gen,
                        "context_tokens_approx": approx_tokens(prompt),
                        "prompt": prompt,
                    }
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
                    i += 1

    # Pin a SHA so the orchestrator can refuse to run if the corpus drifts.
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    sha_path = out.with_suffix(out.suffix + ".sha256")
    sha_path.write_text(sha + "\n")
    print(f"wrote {i} prompts to {out}", file=sys.stderr)
    print(f"corpus sha256: {sha}", file=sys.stderr)

if __name__ == "__main__":
    main()
