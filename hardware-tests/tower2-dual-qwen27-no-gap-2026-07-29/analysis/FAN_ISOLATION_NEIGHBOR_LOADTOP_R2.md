# Lower-neighbor fan assistance with the top GPU loaded - R2

The second neighbor-airflow block rotated the lower-fan order to
50% -> 70% -> 30%. GPU1/top remained saturated at 300 W and fixed 50% own
fan while GPU0/bottom remained idle. All three independently initialized
15-minute cells passed every quality, safety, workload-isolation, physical
fan/RPM, independent-clock, steady-state, and cleanup gate.

| Lower fan | Lower RPM | Upper mean / last-5m temp | Upper mean / last-5m clock | Mean request duration | Lower idle power |
|---:|---:|---:|---:|---:|---:|
| 30% | 1,200.029 | 54.915 / 55.675 C | 1,029.362 / 1,025.960 MHz | 27.296 s | 19.106 W |
| 50% | 1,677.978 | 52.153 / 52.894 C | 1,040.874 / 1,038.730 MHz | 27.009 s | 20.218 W |
| 70% | 2,157.009 | 49.882 / 50.042 C | 1,046.191 / 1,043.400 MHz | 26.830 s | 22.741 W |

The 70%-minus-30% contrast was -5.033 C mean upper temperature,
-5.633 C last-five-minute upper temperature, +16.829 MHz mean clock,
+17.440 MHz last-five-minute clock, -0.466 seconds mean request duration,
and +3.635 W idle lower-card power. The direction is monotonic across all
three settings.

R2 independently reproduces R1 despite reversed order. The 50% upper mean
temperature differs from R1 by only +0.033 C and the 70% point by +0.058 C.
This remains `n=2/3`; the third Latin-order block is required before fitting
the first validated neighbor-assistance coefficient.

Artifacts: [`CSV`](fan-isolation-neighbor-loadtop-r2.csv) and
[`figure`](fan-isolation-neighbor-loadtop-r2.png).
