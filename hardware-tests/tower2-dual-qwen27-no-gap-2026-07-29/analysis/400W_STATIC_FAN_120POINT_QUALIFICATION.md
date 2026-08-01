# 400/400 W 120-point fan-budget qualification

The prospectively amended 120-point fan budget passed all three independent
two-minute safety bumps at 400/400 W. Every cell held both GPUs at 100%
utilization and approximately 400 W, tracked its commanded fan settings, and
recorded zero software/hardware thermal-slowdown or hardware-power-brake
events and zero within-run thermal/brake counter deltas.

| Policy | Bottom fan / RPM | Top fan / RPM | Bottom mean / max C | Top mean / max C | Bottom / top mean clock MHz |
|---|---:|---:|---:|---:|---:|
| EQ60 | 60% / 1,917 | 60% / 1,917 | 60.633 / 64 | 72.874 / 76 | 1,763.771 / 1,583.936 |
| B50T70 | 50% / 1,679 | 70% / 2,158 | 58.327 / 62 | 70.218 / 75 | 1,788.282 / 1,611.296 |
| B70T50 | 70% / 2,158 | 50% / 1,678 | 58.006 / 62 | 70.351 / 74 | 1,774.998 / 1,619.146 |

The 120-point budget is substantially safer in the short window than the
retired 100-point 400 W budget: the hottest top observation was 76 C, leaving
9 C to the unchanged 85 C cutoff. All three cells remained thermally
non-steady, however. The directional policies were nearly tied in top mean
temperature (0.133 C apart), and their short-run clock/throughput ordering is
not inferential. These bumps authorize, but cannot replace, the three
pre-registered 15-minute Latin-order blocks.

Artifacts:

- [`400w-static-fan-120point-qualification.csv`](400w-static-fan-120point-qualification.csv)
- [`400w-static-fan-120point-qualification.png`](400w-static-fan-120point-qualification.png)
- [`../ng-fan-eq60-sym400-v3host-bump-r1/`](../ng-fan-eq60-sym400-v3host-bump-r1/)
- [`../ng-fan-b50t70-sym400-v3host-bump-r1/`](../ng-fan-b50t70-sym400-v3host-bump-r1/)
- [`../ng-fan-b70t50-sym400-v3host-bump-r1/`](../ng-fan-b70t50-sym400-v3host-bump-r1/)
- [`../static-fan-power-sym400-fan120-qualify-r1/`](../static-fan-power-sym400-fan120-qualify-r1/)
