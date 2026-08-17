# Card evidence — pinned-revision sampler ground truth

Firsthand record of the model-card fetches backing PREREGISTRATION.md section 1.
Re-fetched and hashed 2026-08-16 (UTC) from tower2 (192.168.0.175) with
`curl -sS -L https://huggingface.co/Qwen/<model>/raw/<revision>/<file>`.
Raw fetched copies retained at `/home/michael/card-evidence-fetch/` on tower2.

## Fetched files

| model | pinned revision | file | sha256 | bytes |
|---|---|---|---|---|
| `Qwen/Qwen3.6-27B` | `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` | `README.md` | `bb936d6da51014f1edc9aa4cf9abf28d98695b7616ad56adfeeebfa752051d3d` | 62593 |
| `Qwen/Qwen3.6-27B` | `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` | `generation_config.json` | `e70c136c1b78ddc1fb0905bac8e733a4dc448d4f852a5dd75143fffc70be550e` | 202 |
| `Qwen/Qwen3.8-27B` | `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0` | `README.md` | `57e4bdb258ee1a7d2635c5174ebd4e56abe392505cdb5f8bbb356b0dc4293641` | 65012 |
| `Qwen/Qwen3.8-27B` | `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0` | `generation_config.json` | `e70c136c1b78ddc1fb0905bac8e733a4dc448d4f852a5dd75143fffc70be550e` | 202 |

All four fetches returned HTTP 200. The two `generation_config.json` files are
**byte-identical** (same sha256).

## generation_config.json bodies (verbatim, identical for both models)

```json
{
    "bos_token_id": 248044,
    "do_sample": true,
    "eos_token_id": [
        248046,
        248044
    ],
    "pad_token_id": 248044,
    "temperature": 1.0,
    "top_k": 20,
    "top_p": 0.95
}
```

Note: `generation_config.json` carries only `temperature/top_k/top_p`
(T1.0 / top_k 20 / top_p 0.95) — the **thinking**-mode values. It contains no
`min_p`, no `presence_penalty`, no `repetition_penalty`, and no non-thinking
profile. The official non-thinking sampler exists **only** in the README prose
quoted below. Any harness that "uses the model defaults" therefore runs the
thinking sampler regardless of thinking mode — the exact defect the corrective
study fixes.

## Qwen3.6-27B README @ 6a9e13bd — sampler recommendation (lines 635-637)

```
635  > - Thinking mode for general tasks: `temperature=1.0, top_p=0.95, top_k=20, min_p=0.0, presence_penalty=0.0, repetition_penalty=1.0`
636  > - Thinking mode for precise coding tasks (e.g. WebDev): `temperature=0.6, top_p=0.95, top_k=20, min_p=0.0, presence_penalty=0.0, repetition_penalty=1.0`
637  > - Instruct (or non-thinking) mode: `temperature=0.7, top_p=0.80, top_k=20, min_p=0.0, presence_penalty=1.5, repetition_penalty=1.0`
```

(The same three profiles are restated in a best-practices section at
L976/L978/L980.)

## Qwen3.8-27B README @ 1d4bf0f2 — sampler recommendation (lines 252-253)

```
252  > - Thinking Mode: `temperature=1.0`, `top_p=0.95`, `top_k=20`, `min_p=0.0`, `presence_penalty=0.0`, `repetition_penalty=1.0`
253  > - Instruct (or non-thinking) mode: `temperature=0.7`, `top_p=0.80`, `top_k=20`, `min_p=0.0`, `presence_penalty=1.5`, `repetition_penalty=1.0`
```

(Restated verbatim at L502-503.)

## Qwen3.8-27B README @ 1d4bf0f2 — reasoning_effort and preserve_thinking

Lines 258-261:

```
258  Qwen3.8 comes with official support for `reasoning_effort`, which can be used to adjust reasoning depth and control cost:
259    - `xhigh` (default): for complex tasks demanding thorough analysis
260    - `medium`: balancing accuracy and speed
261    - `low`: efficient reasoning optimizing for speed and cost
```

Line 264:

```
264  In addition, `preserve_thinking` is enabled by default for all workloads for the best out-of-the-box experience. To disable preserved thinking, refer to the examples [here](#disable-preserved-thinking).
```

Thinking-mode worked example, lines 294-302 (defaults made explicit in the
card's own comments):

```
294      extra_body={
295          "chat_template_kwargs": {
296              "enable_thinking": True,  # on by default
297              "preserve_thinking": True, # on by default
298          },
299      },
300      reasoning_effort="xhigh",  # xhigh by default; supported levels are xhigh, medium, and low
301      stream=True,
302      stream_options={"include_usage": True},
```

## Qwen3.8-27B README @ 1d4bf0f2 — non-thinking worked example (lines 451-461)

```
451  chat_response = client.chat.completions.create(
452      model="Qwen/Qwen3.8-27B",
453      messages=messages,
454      temperature=0.7,
455      top_p=0.8,
456      presence_penalty=1.5,
457      extra_body={
458          "top_k": 20,
459          "chat_template_kwargs": {"enable_thinking": False},
460      },
461  )
```

PREREGISTRATION.md section 1 cites this worked example as "L452-460"; the
fenced client call in the file as fetched spans L451-461 (same content, the
call opens one line earlier). Sampler-line citations L635-637 (3.6) and
L252-253 (3.8) match the fetched files exactly.

## Conclusions this record supports

1. The official **non-thinking** samplers of Qwen3.6-27B and Qwen3.8-27B are
   **identical**: T0.7 / top_p 0.80 / top_k 20 / min_p 0.0 /
   presence_penalty 1.5 / repetition_penalty 1.0 (3.6 L637; 3.8 L253 + worked
   example L451-461).
2. The official **thinking** samplers are identical: T1.0 / top_p 0.95 /
   top_k 20 / min_p 0.0 / presence_penalty 0.0 / repetition_penalty 1.0
   (3.6 L635; 3.8 L252). Qwen3.6 additionally documents a T0.6 coding-thinking
   variant (L636) which this study does not run.
3. Qwen3.8 exposes `reasoning_effort` with default `xhigh` (supported: xhigh,
   medium, low) and `preserve_thinking` default on (L258-264, L294-302) —
   grounds for the protocol's xhigh-only + preserve_thinking=true 3.8
   official-think arm.
4. `generation_config.json` (identical bytes for both models) encodes only the
   thinking-mode T1.0/0.95/20 values — no non-thinking profile ships in config.
