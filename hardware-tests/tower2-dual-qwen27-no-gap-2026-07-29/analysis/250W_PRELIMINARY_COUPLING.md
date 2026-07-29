# Preliminary 250 W directional-coupling comparison

This comparison combines the equal 250/250 W cell with the bottom-loaded/top-idle 250 W isolation cell. Both used the same no-gap physical layout and Qwen3.6-27B workload. The comparison is preliminary because room and local inlet temperatures were not instrumented, the cells were not randomized replicates, and the top-loaded/bottom-idle direction is still pending.

## Matched bottom-load comparison

| Metric | Bottom 250 W, top idle | Both loaded at 250 W | Change caused by adding top workload |
|---|---:|---:|---:|
| GPU0/bottom mean temperature | 52.414°C | 51.849°C | -0.565°C |
| GPU0/bottom last-5-minute temperature | 53.031°C | 52.049°C | -0.982°C |
| GPU0/bottom mean fan | 31.021% | 30.673% | -0.348 pp |
| GPU1/top mean power | 21.809 W | 249.994 W | +228.185 W |
| GPU1/top mean temperature | 43.137°C | 66.969°C | +23.832°C |
| GPU1/top last-5-minute temperature | 44.805°C | 68.167°C | +23.362°C |
| GPU1/top mean fan | 30.000% | 40.146% | +10.146 pp |

Adding approximately 228 W of workload to the top card increased its last-five-minute temperature by 23.36°C despite a 10.15-point fan response. The bottom card changed by -0.98°C rather than heating measurably. That negative value must not be interpreted as cooling caused by the top card; it is evidence that top-to-bottom coupling at this operating point is smaller than the uncontrolled between-run variation.

Within the bottom-only run, the idle top card rose from a 31°C pre-run core temperature to a 44.805°C last-five-minute mean while the bottom card held 250 W. This +13.805°C transient is strong evidence of bottom-to-top coupling, although it is not a thermal resistance because the start temperature is not a measured local inlet and bottom idle power was not sampled as a full control window.

## Current inference

The two available cells support a strongly directional air-path model: bottom-card heat materially warms the top position, whereas adding top-card heat did not produce a resolvable bottom-position penalty at 250 W. The top-loaded/bottom-idle cell and randomized repeats are required before assigning directional coupling coefficients or uncertainty intervals.

Machine-readable deltas are in [`250w-coupling-preliminary.csv`](250w-coupling-preliminary.csv).
