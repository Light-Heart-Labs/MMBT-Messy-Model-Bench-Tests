# PR #750 — Summary

## Title (verbatim)

> feat: AMD Multi-GPU Support

## Author's stated motivation

End-to-end multi-GPU support for AMD GPUs, matching the existing NVIDIA
multi-GPU feature set. AMD support was previously single-GPU only. This
PR adds: hardware discovery (sysfs `vendor=0x1002` enumeration, XCP virtual-
card filtering on MI300X, total-VRAM aggregation), topology analysis
(amd-smi JSON / rocm-smi text / sysfs NUMA fallback with link classification:
XGMI, PCIe-SameSwitch, PCIe-HostBridge, PCIe-CrossNUMA), GPU assignment,
Docker Compose isolation, CLI commands (`dream gpu` family already on
NVIDIA, now AMD-aware), and dashboard-api monitoring.

The author reports testing on real hardware: 4× AMD Instinct MI300X.

## Auditor's one-line restatement

> Adds the AMD-side counterpart of the existing NVIDIA multi-GPU stack
> (topology, assignment, compose overlays, CLI, monitoring), with the
> single non-AMD-specific change being a rename of the generic
> `multigpu.{yml,yaml}` files to `multigpu-nvidia.{yml,yaml}` for symmetry
> and an upgrade-cache-flush handler so existing NVIDIA installs don't
> hit a missing-file error after upgrade.

## Bounty tier (claimed / inferred)

Inferred Large ($400) — multi-system, ~3,000 added lines, real-hardware
test fixtures, new lib, new compose overlays, dashboard integration. The
scope-vs-tier match looks correct.
