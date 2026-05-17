#!/usr/bin/env python3
"""Compute local-AI hardware valuation metrics from editable price inputs.

This script intentionally keeps prices out of prose. Update the systems CSV
when the market moves, rerun this script, and review the generated ratios.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


DEFAULT_SYSTEMS = Path(
    "hardware-tests/local-ai-hardware-valuation-2026-05-17/inputs/systems.csv"
)
DEFAULT_HEADLINE = Path(
    "hardware-tests/qwen3.6-q8-fleet-2026-05-17/aggregate/headline.csv"
)
DEFAULT_OUTPUT = Path(
    "hardware-tests/local-ai-hardware-valuation-2026-05-17/outputs/valuation.csv"
)


OUTPUT_COLUMNS = [
    "system_id",
    "display_name",
    "category",
    "price_usd",
    "price_asof",
    "price_basis",
    "memory_gb_for_value",
    "memory_bandwidth_gbps",
    "price_per_memory_gb_usd",
    "price_per_bandwidth_gbps_usd",
    "capacity_bandwidth_score",
    "price_per_capacity_bandwidth_score_usd",
    "mmbt_27b_q8_backend",
    "mmbt_27b_q8_peak_decode_tps",
    "price_per_mmbt_decode_tps_usd",
    "mmbt_decode_tps_per_1k_usd",
    "mmbt_27b_q8_peak_prefill_tps",
    "price_per_mmbt_prefill_tps_usd",
    "mmbt_prefill_tps_per_1k_usd",
    "wall_w_reference",
    "wall_w_status",
    "five_year_energy_usd_at_12c",
    "five_year_tco_usd_at_12c",
    "measurement_source",
    "price_source_url",
    "spec_source_url",
    "notes",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate hardware valuation ratios from systems.csv and MMBT headline.csv."
    )
    parser.add_argument("--systems", type=Path, default=DEFAULT_SYSTEMS)
    parser.add_argument("--headline", type=Path, default=DEFAULT_HEADLINE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def as_float(value: str | None) -> float | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    return float(value)


def ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def fmt(value: float | None, places: int = 2) -> str:
    if value is None:
        return ""
    return f"{value:.{places}f}"


def headline_index(rows: list[dict[str, str]]) -> dict[tuple[str, str, str], dict[str, str]]:
    return {
        (row["host"], row["model"], row["backend"]): row
        for row in rows
    }


def valuation_row(
    system: dict[str, str],
    measurements: dict[tuple[str, str, str], dict[str, str]],
) -> dict[str, str]:
    price = as_float(system.get("price_usd"))
    memory_gb = as_float(system.get("memory_gb_for_value"))
    bandwidth = as_float(system.get("memory_bandwidth_gbps"))
    wall_w = as_float(system.get("wall_w_reference"))

    key = (
        system.get("measurement_host", "").strip(),
        system.get("measurement_model", "").strip(),
        system.get("measurement_backend", "").strip(),
    )
    measured = measurements.get(key) if all(key) else None

    decode_tps = as_float(measured.get("peak_decode_tps")) if measured else None
    prefill_tps = as_float(measured.get("peak_prefill_tps")) if measured else None

    capacity_bandwidth = (
        memory_gb * bandwidth
        if memory_gb is not None and bandwidth is not None
        else None
    )
    energy_5y = None
    if wall_w is not None:
        energy_5y = wall_w * 24 * 365 * 5 / 1000 * 0.12

    measurement_source = ""
    if measured:
        measurement_source = (
            f"hardware-tests/qwen3.6-q8-fleet-2026-05-17/aggregate/headline.csv"
            f"::{key[0]}/{key[1]}/{key[2]}"
        )

    return {
        "system_id": system["system_id"],
        "display_name": system["display_name"],
        "category": system["category"],
        "price_usd": fmt(price, 2),
        "price_asof": system["price_asof"],
        "price_basis": system["price_basis"],
        "memory_gb_for_value": fmt(memory_gb, 2),
        "memory_bandwidth_gbps": fmt(bandwidth, 2),
        "price_per_memory_gb_usd": fmt(ratio(price, memory_gb), 2),
        "price_per_bandwidth_gbps_usd": fmt(ratio(price, bandwidth), 2),
        "capacity_bandwidth_score": fmt(capacity_bandwidth, 2),
        "price_per_capacity_bandwidth_score_usd": fmt(ratio(price, capacity_bandwidth), 6),
        "mmbt_27b_q8_backend": system.get("measurement_backend", ""),
        "mmbt_27b_q8_peak_decode_tps": fmt(decode_tps, 3),
        "price_per_mmbt_decode_tps_usd": fmt(ratio(price, decode_tps), 2),
        "mmbt_decode_tps_per_1k_usd": fmt(ratio(decode_tps, price / 1000 if price else None), 2),
        "mmbt_27b_q8_peak_prefill_tps": fmt(prefill_tps, 3),
        "price_per_mmbt_prefill_tps_usd": fmt(ratio(price, prefill_tps), 2),
        "mmbt_prefill_tps_per_1k_usd": fmt(ratio(prefill_tps, price / 1000 if price else None), 2),
        "wall_w_reference": fmt(wall_w, 2),
        "wall_w_status": system.get("wall_w_status", ""),
        "five_year_energy_usd_at_12c": fmt(energy_5y, 2),
        "five_year_tco_usd_at_12c": fmt(price + energy_5y if price is not None and energy_5y is not None else None, 2),
        "measurement_source": measurement_source,
        "price_source_url": system.get("price_source_url", ""),
        "spec_source_url": system.get("spec_source_url", ""),
        "notes": system.get("notes", ""),
    }


def main() -> None:
    args = parse_args()
    systems = read_csv(args.systems)
    measurements = headline_index(read_csv(args.headline))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for system in systems:
            writer.writerow(valuation_row(system, measurements))


if __name__ == "__main__":
    main()
