#!/usr/bin/env node
// Read the combined CSV and emit a Markdown per-cap summary table for findings.md.
//
// Usage: node render-table.mjs <combined.csv>

import fs from "fs";

const csvPath = process.argv[2] ?? "ltx-power-sweep-combined.csv";
const text = fs.readFileSync(csvPath, "utf-8").trim();
const lines = text.split("\n");
const header = lines.shift().split(",");
const idx = Object.fromEntries(header.map((h, i) => [h, i]));

const rows = lines
  .map((l) => l.split(","))
  .filter((r) => !r[idx.error]);

const byCap = new Map();
for (const r of rows) {
  const cap = parseInt(r[idx.cap_w], 10);
  if (!byCap.has(cap)) byCap.set(cap, []);
  byCap.get(cap).push({
    render_ms: parseInt(r[idx.render_ms], 10),
    peak_w: parseFloat(r[idx.gpu0_power_peak_w]),
    avg_w: parseFloat(r[idx.gpu0_power_avg_w]),
    temp_peak: parseInt(r[idx.gpu0_temp_peak_c], 10),
  });
}

const caps = [...byCap.keys()].sort((a, b) => b - a);
const stats = caps.map((cap) => {
  const xs = byCap.get(cap);
  const ms = xs.map((x) => x.render_ms).sort((a, b) => a - b);
  return {
    cap,
    n: xs.length,
    mean: ms.reduce((a, b) => a + b, 0) / ms.length,
    median: ms[Math.floor(ms.length / 2)],
    min: ms[0],
    max: ms[ms.length - 1],
    peak: xs.reduce((a, b) => a + b.peak_w, 0) / xs.length,
    avg: xs.reduce((a, b) => a + b.avg_w, 0) / xs.length,
    tmax: Math.max(...xs.map((x) => x.temp_peak)),
  };
});

const ref600 = stats.find((s) => s.cap === 600)?.mean;
const ref500 = stats.find((s) => s.cap === 500)?.mean;

console.log(
  "| Cap (W) | Runs | Mean (s) | Median (s) | Min (s) | Max (s) | Mean peak draw (W) | Mean avg draw (W) | Peak temp (°C) | Δ vs 600 W | Δ vs 500 W |",
);
console.log(
  "|---|---|---|---|---|---|---|---|---|---|---|",
);
for (const s of stats) {
  const d600 = ref600 ? `${((s.mean - ref600) / ref600 * 100).toFixed(1)}%` : "—";
  const d500 = ref500 ? `${((s.mean - ref500) / ref500 * 100).toFixed(1)}%` : "—";
  const d600s = s.cap === 600 ? "0% (ref)" : (s.mean > ref600 ? "+" : "") + d600;
  const d500s = s.cap === 500 ? "0% (ref)" : (s.mean > ref500 ? "+" : "") + d500;
  console.log(
    `| ${s.cap} | ${s.n} | ${(s.mean / 1000).toFixed(2)} | ${(s.median / 1000).toFixed(2)} | ${(s.min / 1000).toFixed(2)} | ${(s.max / 1000).toFixed(2)} | ${s.peak.toFixed(0)} | ${s.avg.toFixed(0)} | ${s.tmax} | ${d600s} | ${d500s} |`,
  );
}
