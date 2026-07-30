# Fixed-fan 250/250 W bump R1 — instrumentation failure

- Run: `2026-07-30T02-51-10Z-ng-fan-eq30-sym250-bump`
- Cell: `NG-FAN-EQ30-SYM250-BUMP`
- Requested policy: GPU0/bottom 30%, GPU1/top 30%
- Result: **ABORTED / EXCLUDED before the measured window**

The run completed a 304-second uninterrupted quiescent soak and started from
28°C bottom / 31°C top. After the GPU0 Qwen engine became ready, the first
fixed-fan implementation invoked the driver-matched `nvidia-settings` client
as the display user. NV-CONTROL printed `Operation not permitted`, but returned
a successful process status. Because every fan was already at the requested
30% idle floor, the original target/current check falsely appeared to pass.

The issue was noticed during the 60-second warmup. The parent test process was
terminated before any measured samples were admitted. This directory therefore
contains only a partial warmup trace and **must not be used as fixed-fan thermal
evidence**.

Cleanup removed the temporary GPU0 engine, restarted Sanctuary to clear
admitted requests, restored both 600 W power limits and stopped services, and
confirmed both `GPUFanControlState` values were `0` (automatic).

The harness was corrected to:

1. run NV-CONTROL assignments with root privilege while using GDM's Xauthority;
2. require the card's explicit manual-control state to read `1`;
3. require both physical fans to reach their commanded target with nonzero RPM;
4. restore and verify automatic state on every exit.

R2 is the first valid fixed-fan loaded bump.
