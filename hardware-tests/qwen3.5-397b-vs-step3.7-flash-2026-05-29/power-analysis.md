## Power behavior (dual RTX PRO 6000 Blackwell, 600W/GPU cap)

From 7792 samples (3896 paired) captured during the run. Per-GPU:

| GPU | mean | p50 | p90 | p99 | max | %of cap | mean util |
|---|--:|--:|--:|--:|--:|--:|--:|
| GPU0 | 305 | 346 | 364 | 522 | **539** | 90% | 39% |
| GPU1 | 278 | 324 | 334 | 450 | **475** | 79% | 39% |

**Combined both-GPU draw:** median 670W (56% of 1200W cap), p90 694W, max **985W (82%)**.
Samples within 5% of full (1140W): **0 / 3896 (0.0%)**.

**Draw by phase:** decode bursts (util>20%) mean 339W/GPU; CPU-tool / idle phases (util<5%) mean 122W/GPU.

**GPU0 vs GPU1:** GPU0 averages 305W vs GPU1 278W (+27W). Pipeline-parallel (`-sm layer`) loads layers across cards in sequence, so the two rarely peak together — the combined draw never approaches the 1200W ceiling.
