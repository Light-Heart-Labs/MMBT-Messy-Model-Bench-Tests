# 400/400 W 100-point fan-budget boundary

The first 400 W measured block established that the 100-point static fan
budget used at 350 W cannot be carried upward unchanged.

- EQ50 completed 15 minutes and passed every gate, but GPU1/top reached 84 C,
  only 1 C below the static-spine cutoff.
- B60T40 reached 85 C after approximately four measured minutes with GPU1/top
  fixed at 40% / 1,439 RPM. Its temperature was still rising at approximately
  2.091 C/min, so the cell was not approaching a safe plateau.
- The fail-stop block did not run B40T60 after B60T40 failed.
- Both executed cells held approximately 400 W and 100% utilization.
- Neither cell recorded an active slowdown/brake sample or a within-run
  thermal/brake counter delta.

This separates two concepts that are often conflated: the hardware had not
yet asserted NVIDIA's thermal-slowdown mechanisms, but the operating point
was already outside this campaign's safe, repeatable envelope. Raising the
cutoff would weaken the research design and is not justified.

The result also bounds the 350 W controller finding. At 350 W, reallocating a
100-point budget toward the lower card improved the upper card. At 400 W, the
same 60/40 allocation leaves too little upper-card local airflow to remain
below 85 C. Stack assistance is real, but it does not replace the downstream
card's minimum local-flow requirement as heat density rises.

Before any replacement run, the prospective protocol was amended to use a
matched 120-point budget: EQ60, B70T50, and B50T70. These retain the allocation
experiment while increasing every corresponding local fan by 10 points. All
three require new qualification and three Latin-order blocks before inference.

Artifacts:

- [`../ng-fan-eq50-sym400-v3host-15m-r1/`](../ng-fan-eq50-sym400-v3host-15m-r1/)
- [`../ng-fan-b60t40-sym400-v3host-15m-r1/`](../ng-fan-b60t40-sym400-v3host-15m-r1/)
- [`../static-fan-power-sym400-measure-r1/`](../static-fan-power-sym400-measure-r1/)
