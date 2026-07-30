# Bottom-card own-fan isolation - saturated 300 W block R1

This is the first independently initialized 30/50/70% own-fan block with
GPU0/bottom saturated at 300 W and GPU1/top left model-resident but idle at a
fixed 50% fan setting. The Latin order is 30/50/70 for R1, 50/70/30 for R2,
and 70/30/50 for R3. Each cell passed all frozen V3HOST quality gates, but each
is only `n=1/3`; the contrasts below are preliminary and execution order is
still aliased with fan setting.

## Observed response

| Bottom fan | Mean RPM | Bottom mean / last-5m temp | Bottom mean / last-5m clock | Mean request duration | Idle-top mean temp |
|---:|---:|---:|---:|---:|---:|
| 30% | 1,200.100 | 56.449 / 56.915 C | 1,025.734 / 1,023.009 MHz | 26.785 s | 44.978 C |
| 50% | 1,678.064 | 53.337 / 53.562 C | 1,028.783 / 1,026.112 MHz | 26.705 s | 41.876 C |
| 70% | 2,157.122 | 50.814 / 51.048 C | 1,025.235 / 1,021.903 MHz | 26.810 s | 39.388 C |

All three cells held 299.993 W mean board power, 100% utilization, 1.2089
requests/s, complete fan/RPM telemetry, independent clock agreement, and zero
thermal or brake events/counter growth.

## Preliminary contrasts

Increasing the bottom card from 30% to 50% added 477.964 RPM, reduced its mean
temperature by 3.112 C, raised mean clock by 3.049 MHz, and reduced mean
request duration by 0.080 seconds. Increasing from 50% to 70% added another
479.058 RPM and removed another 2.523 C, but mean clock fell 3.548 MHz and mean
request duration increased 0.105 seconds.

The idle top card also cooled monotonically as only the bottom card's fans were
raised: 44.978, 41.876, then 39.388 C. That is direct preliminary evidence
that the bottom fans alter the shared no-gap airflow and help reject heat from
the adjacent top-card region, rather than cooling only the loaded bottom die.

The thermal response is already large and monotonic. The clock/performance
response is small and non-monotonic, with the best observed operating point at
50%, not 70%. Plausible mechanisms include fan electrical power sharing inside
the fixed board-power envelope, voltage/boost-bin behavior, or ordinary
block/order variation. R2 and R3 intentionally rotate execution order so that
the campaign can distinguish a repeatable high-RPM tradeoff from time and
chassis-state drift.

Machine-readable source:
[`fan-isolation-own-bottom-r1.csv`](fan-isolation-own-bottom-r1.csv).
The block manifest and launch audit are preserved in
[`../fan-isolation-own-saturated-loadbottom-r1/`](../fan-isolation-own-saturated-loadbottom-r1/).
