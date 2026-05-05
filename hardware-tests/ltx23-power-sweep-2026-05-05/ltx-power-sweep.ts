// LTX-2.3 GPU0 power-cap sweep.
//
// Sweeps GPU0 power cap from 600W → 400W in 10W steps and runs the
// "founder gets an idea at sunrise" video prompt N times per cap. Logs
// render time + power/clock/temp envelope per run to a CSV. At end,
// prints a per-cap summary so we can see whether raising the cap above
// the current 500W operating point buys faster generations, and how much
// dropping below it costs.
//
// Usage (from ~/dream-expo):
//   node --experimental-strip-types scripts/bench/ltx-power-sweep.ts
//
// Optional flags:
//   --caps=600,580,500     Custom cap list (default 600..400 step 10)
//   --n=3                  Runs per cap (default 3)
//   --out=path.csv         CSV path (default output/ltx-power-sweep-<ts>.csv)
//   --settle-ms=5000       Sleep after cap change (default 5000)
//   --gap-ms=1500          Sleep between runs at same cap (default 1500)
//   --dry-run              Skip cap changes (for testing the harness)
//
// Requires sudo for `nvidia-smi -pl`. Pre-warm your sudo cache before
// running (`sudo -v`); the script then heartbeats every 60s so cap
// changes stay non-interactive throughout. Cap is restored to 500W on
// normal exit AND on SIGINT/SIGTERM.

import { spawn, spawnSync, type ChildProcess } from "child_process";
import { promises as fs } from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { buildLtxWorkflow } from "../../src/lib/ltx-workflow.ts";

const COMFY_URL = process.env.COMFY_URL ?? "http://127.0.0.1:8188";
const RESTORE_CAP_W = 500;

// Verbatim from src/app/video/page.tsx — "A founder getting an idea at sunrise".
const SUNRISE_PROMPT =
  "Cinematic close-up shot, the camera slowly pushing in on a young founder seated at a wooden workbench, their hand pausing mid-sketch over an open notebook, eyes lifting toward soft warm sunrise light streaming in through tall industrial windows, a quiet moment of realization crossing their face, motes of dust drifting in the beams, a coffee mug beside them, prototyping tools and a laptop softly out of focus in the background, shallow depth of field, photorealistic detail, cinematic warm color grade, no camera shake, no warping, no rolling shutter, 8K sharp focus.";

// ---- args ----------------------------------------------------------------

function parseArgs(argv: string[]): Record<string, string | boolean> {
  const out: Record<string, string | boolean> = {};
  for (const a of argv) {
    if (!a.startsWith("--")) continue;
    const [k, v] = a.slice(2).split("=", 2);
    out[k] = v ?? true;
  }
  return out;
}

const args = parseArgs(process.argv.slice(2));

const CAPS: number[] = (args.caps as string | undefined)
  ? (args.caps as string).split(",").map((s) => parseInt(s.trim(), 10))
  : [
      600, 590, 580, 570, 560, 550, 540, 530, 520, 510, 500,
      490, 480, 470, 460, 450, 440, 430, 420, 410, 400,
    ];

const N = parseInt((args.n as string | undefined) ?? "3", 10);
const SETTLE_MS = parseInt((args["settle-ms"] as string | undefined) ?? "5000", 10);
const GAP_MS = parseInt((args["gap-ms"] as string | undefined) ?? "1500", 10);
const DRY_RUN = !!args["dry-run"];

const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT_DIR = path.join(HERE, "output");
const TS = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
const OUT_PATH =
  (args.out as string | undefined) ??
  path.join(OUT_DIR, `ltx-power-sweep-${TS}.csv`);

// ---- types ---------------------------------------------------------------

type RunRow = {
  cap_w: number;
  run_idx: number;
  prompt_id: string;
  submitted_at_ms: number;
  finished_at_ms: number;
  render_ms: number;
  gpu0_power_avg_w: number;
  gpu0_power_peak_w: number;
  gpu0_clock_avg_mhz: number;
  gpu0_temp_start_c: number;
  gpu0_temp_peak_c: number;
  sample_count: number;
  error: string;
};

const CSV_HEADER = [
  "cap_w",
  "run_idx",
  "prompt_id",
  "submitted_at_ms",
  "finished_at_ms",
  "render_ms",
  "gpu0_power_avg_w",
  "gpu0_power_peak_w",
  "gpu0_clock_avg_mhz",
  "gpu0_temp_start_c",
  "gpu0_temp_peak_c",
  "sample_count",
  "error",
].join(",");

function rowToCsv(r: RunRow): string {
  return [
    r.cap_w,
    r.run_idx,
    r.prompt_id,
    r.submitted_at_ms,
    r.finished_at_ms,
    r.render_ms,
    r.gpu0_power_avg_w.toFixed(1),
    r.gpu0_power_peak_w.toFixed(1),
    r.gpu0_clock_avg_mhz.toFixed(0),
    r.gpu0_temp_start_c,
    r.gpu0_temp_peak_c,
    r.sample_count,
    r.error.replace(/[,\n]/g, " "),
  ].join(",");
}

// ---- sudo ---------------------------------------------------------------

let sudoKeepalive: NodeJS.Timeout | null = null;

function sudoAuthenticate(): void {
  if (DRY_RUN) return;
  const r = spawnSync("sudo", ["-n", "-v"], { stdio: "pipe", encoding: "utf-8" });
  if (r.status !== 0) {
    throw new Error(
      `sudo cache empty — run \`sudo -v\` in your shell first, then rerun this script. (${(r.stderr || r.stdout).trim()})`,
    );
  }
  sudoKeepalive = setInterval(() => {
    spawnSync("sudo", ["-n", "-v"], { stdio: "ignore" });
  }, 60_000);
}

function sudoStop(): void {
  if (sudoKeepalive) {
    clearInterval(sudoKeepalive);
    sudoKeepalive = null;
  }
}

// ---- power cap ----------------------------------------------------------

function setPowerCap(w: number): void {
  if (DRY_RUN) {
    console.log(`  [dry-run] would set GPU0 power cap to ${w}W`);
    return;
  }
  const r = spawnSync(
    "sudo",
    ["-n", "nvidia-smi", "-i", "0", "-pl", String(w)],
    { stdio: "pipe", encoding: "utf-8" },
  );
  if (r.status !== 0) {
    throw new Error(
      `failed to set GPU0 cap to ${w}W: ${(r.stderr || r.stdout).trim()}`,
    );
  }
}

function readCurrentCap(): number {
  const r = spawnSync(
    "nvidia-smi",
    ["-i", "0", "--query-gpu=power.limit", "--format=csv,noheader,nounits"],
    { encoding: "utf-8" },
  );
  return parseFloat(r.stdout.trim());
}

// ---- dmon sampler --------------------------------------------------------

type DmonStats = {
  power_avg: number;
  power_peak: number;
  clock_avg: number;
  temp_start: number;
  temp_peak: number;
  count: number;
};

function startDmon(): { stop: () => Promise<DmonStats> } {
  const proc: ChildProcess = spawn(
    "nvidia-smi",
    ["dmon", "-i", "0", "-s", "pucm", "-d", "1"],
    { stdio: ["ignore", "pipe", "pipe"] },
  );
  let buf = "";
  const samples: { pwr: number; temp: number; pclk: number }[] = [];
  proc.stdout!.on("data", (chunk: Buffer) => {
    buf += chunk.toString();
    const lines = buf.split("\n");
    buf = lines.pop() ?? "";
    for (const line of lines) {
      const t = line.trim();
      if (!t || t.startsWith("#")) continue;
      const cols = t.split(/\s+/);
      // Cols: gpu pwr gtemp mtemp sm mem enc dec jpg ofa mclk pclk fb bar1 ccpm
      const pwr = parseFloat(cols[1]);
      const temp = parseFloat(cols[2]);
      const pclk = parseFloat(cols[11]);
      if (!Number.isFinite(pwr) || !Number.isFinite(temp)) continue;
      samples.push({
        pwr,
        temp,
        pclk: Number.isFinite(pclk) ? pclk : 0,
      });
    }
  });
  proc.stderr!.on("data", () => {});
  return {
    stop: async () => {
      proc.kill("SIGINT");
      await new Promise<void>((resolve) =>
        proc.on("exit", () => resolve()),
      );
      if (samples.length === 0) {
        return {
          power_avg: 0,
          power_peak: 0,
          clock_avg: 0,
          temp_start: 0,
          temp_peak: 0,
          count: 0,
        };
      }
      const power_avg =
        samples.reduce((a, b) => a + b.pwr, 0) / samples.length;
      const power_peak = samples.reduce(
        (m, s) => (s.pwr > m ? s.pwr : m),
        -Infinity,
      );
      const clock_avg =
        samples.reduce((a, b) => a + b.pclk, 0) / samples.length;
      const temp_start = samples[0].temp;
      const temp_peak = samples.reduce(
        (m, s) => (s.temp > m ? s.temp : m),
        -Infinity,
      );
      return {
        power_avg,
        power_peak,
        clock_avg,
        temp_start,
        temp_peak,
        count: samples.length,
      };
    },
  };
}

// ---- one render ---------------------------------------------------------

async function runOne(cap: number, runIdx: number): Promise<RunRow> {
  const seed = Math.floor(Math.random() * 1e9);
  const workflow = buildLtxWorkflow({ prompt: SUNRISE_PROMPT, seed });

  const submittedAt = Date.now();
  let promptId = "";
  let error = "";

  try {
    const submitRes = await fetch(`${COMFY_URL}/prompt`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: workflow,
        client_id: `bench-pwr-${seed}`,
      }),
    });
    if (!submitRes.ok) {
      throw new Error(
        `submit ${submitRes.status}: ${(await submitRes.text()).slice(0, 200)}`,
      );
    }
    const submitJson = (await submitRes.json()) as { prompt_id?: string };
    if (!submitJson.prompt_id) throw new Error("no prompt_id in submit");
    promptId = submitJson.prompt_id;
  } catch (e) {
    return {
      cap_w: cap,
      run_idx: runIdx,
      prompt_id: "",
      submitted_at_ms: submittedAt,
      finished_at_ms: submittedAt,
      render_ms: 0,
      gpu0_power_avg_w: 0,
      gpu0_power_peak_w: 0,
      gpu0_clock_avg_mhz: 0,
      gpu0_temp_start_c: 0,
      gpu0_temp_peak_c: 0,
      sample_count: 0,
      error: `submit: ${(e as Error).message}`,
    };
  }

  const dmon = startDmon();

  const TIMEOUT_MS = 5 * 60 * 1000;
  let finishedAt = 0;

  try {
    const start = Date.now();
    while (Date.now() - start < TIMEOUT_MS) {
      await new Promise((r) => setTimeout(r, 500));
      const histRes = await fetch(`${COMFY_URL}/history/${promptId}`);
      if (!histRes.ok) continue;
      const hist = (await histRes.json()) as Record<
        string,
        {
          outputs?: Record<
            string,
            {
              videos?: Array<{ filename: string }>;
              gifs?: Array<{ filename: string }>;
              images?: Array<{ filename: string }>;
            }
          >;
          status?: { completed?: boolean; status_str?: string };
        }
      >;
      const entry = hist[promptId];
      if (!entry) continue;
      if (entry.status?.status_str === "error") {
        error = "ComfyUI reported workflow error";
        finishedAt = Date.now();
        break;
      }
      const outputs = entry.outputs ?? {};
      let foundVideo = false;
      for (const nodeOutputs of Object.values(outputs)) {
        const all = [
          ...(nodeOutputs.videos ?? []),
          ...(nodeOutputs.gifs ?? []),
          ...(nodeOutputs.images ?? []),
        ];
        for (const item of all) {
          if (item.filename && /\.(mp4|webm|mov)$/i.test(item.filename)) {
            foundVideo = true;
            break;
          }
        }
        if (foundVideo) break;
      }
      if (foundVideo) {
        finishedAt = Date.now();
        break;
      }
      if (entry.status?.completed) {
        error = "workflow completed but no video output";
        finishedAt = Date.now();
        break;
      }
    }
    if (finishedAt === 0) {
      error = "timeout waiting for generation";
      finishedAt = Date.now();
    }
  } catch (e) {
    error = `poll: ${(e as Error).message}`;
    finishedAt = Date.now();
  }

  const stats = await dmon.stop();

  return {
    cap_w: cap,
    run_idx: runIdx,
    prompt_id: promptId,
    submitted_at_ms: submittedAt,
    finished_at_ms: finishedAt,
    render_ms: finishedAt - submittedAt,
    gpu0_power_avg_w: stats.power_avg,
    gpu0_power_peak_w: stats.power_peak,
    gpu0_clock_avg_mhz: stats.clock_avg,
    gpu0_temp_start_c: stats.temp_start,
    gpu0_temp_peak_c: stats.temp_peak,
    sample_count: stats.count,
    error,
  };
}

// ---- summary ------------------------------------------------------------

function summarize(rows: RunRow[]): string {
  const byCap = new Map<number, RunRow[]>();
  for (const r of rows) {
    if (r.error) continue;
    if (!byCap.has(r.cap_w)) byCap.set(r.cap_w, []);
    byCap.get(r.cap_w)!.push(r);
  }
  const caps = Array.from(byCap.keys()).sort((a, b) => b - a);
  const lines: string[] = [];
  lines.push(
    "cap_w  n  mean_ms  median_ms  min_ms  max_ms  mean_peak_w  mean_avg_w  peak_temp_c",
  );
  for (const cap of caps) {
    const xs = byCap.get(cap)!;
    const ms = xs.map((r) => r.render_ms).sort((a, b) => a - b);
    const mean = ms.reduce((a, b) => a + b, 0) / ms.length;
    const median = ms[Math.floor(ms.length / 2)];
    const min = ms[0];
    const max = ms[ms.length - 1];
    const peakW =
      xs.reduce((a, b) => a + b.gpu0_power_peak_w, 0) / xs.length;
    const avgW = xs.reduce((a, b) => a + b.gpu0_power_avg_w, 0) / xs.length;
    const peakT = Math.max(...xs.map((r) => r.gpu0_temp_peak_c));
    lines.push(
      [
        cap,
        ms.length,
        mean.toFixed(0),
        median.toFixed(0),
        min,
        max,
        peakW.toFixed(0),
        avgW.toFixed(0),
        peakT,
      ].join("  "),
    );
  }
  // Compare each cap to the 500W baseline if present.
  const baseline = byCap.get(500);
  if (baseline && baseline.length > 0) {
    const baseMean =
      baseline.reduce((a, b) => a + b.render_ms, 0) / baseline.length;
    lines.push("");
    lines.push(`Speedup vs 500W baseline (mean=${baseMean.toFixed(0)}ms):`);
    for (const cap of caps) {
      if (cap === 500) continue;
      const xs = byCap.get(cap)!;
      const m = xs.reduce((a, b) => a + b.render_ms, 0) / xs.length;
      const pct = ((baseMean - m) / baseMean) * 100;
      lines.push(`  ${cap}W  ${m.toFixed(0)}ms  ${pct >= 0 ? "+" : ""}${pct.toFixed(2)}%`);
    }
  }
  return lines.join("\n");
}

// ---- main ---------------------------------------------------------------

async function preflight(): Promise<void> {
  // ComfyUI alive?
  try {
    const r = await fetch(`${COMFY_URL}/system_stats`);
    if (!r.ok) throw new Error(`http ${r.status}`);
  } catch (e) {
    throw new Error(`ComfyUI not reachable at ${COMFY_URL}: ${(e as Error).message}`);
  }
  // Queue empty?
  const q = await fetch(`${COMFY_URL}/queue`);
  const qj = (await q.json()) as {
    queue_running?: unknown[];
    queue_pending?: unknown[];
  };
  const inflight = (qj.queue_running?.length ?? 0) + (qj.queue_pending?.length ?? 0);
  if (inflight > 0) {
    console.warn(
      `WARNING: ComfyUI has ${inflight} item(s) in queue. They'll execute before the bench starts.`,
    );
  }
}

let rows: RunRow[] = [];
let csvHandle: { append: (line: string) => Promise<void>; close: () => Promise<void> } | null = null;

async function openCsv(): Promise<typeof csvHandle> {
  await fs.mkdir(path.dirname(OUT_PATH), { recursive: true });
  const fh = await fs.open(OUT_PATH, "w");
  await fh.write(CSV_HEADER + "\n");
  return {
    append: async (line: string) => {
      await fh.write(line + "\n");
    },
    close: async () => {
      await fh.close();
    },
  };
}

async function gracefulExit(reason: string, code = 0): Promise<never> {
  console.log(`\n[exit] ${reason}`);
  try {
    setPowerCap(RESTORE_CAP_W);
    console.log(`[exit] restored GPU0 cap to ${RESTORE_CAP_W}W`);
  } catch (e) {
    console.error(`[exit] failed to restore cap: ${(e as Error).message}`);
  }
  sudoStop();
  if (csvHandle) await csvHandle.close();
  if (rows.length > 0) {
    console.log("\n=== Summary ===");
    console.log(summarize(rows));
    console.log(`\nCSV: ${OUT_PATH}`);
  }
  process.exit(code);
}

async function main(): Promise<void> {
  console.log("LTX-2.3 GPU0 power-cap sweep");
  console.log(`Caps:        ${CAPS.join(", ")} W`);
  console.log(`N per cap:   ${N}`);
  console.log(`Total runs:  ${CAPS.length * N}`);
  console.log(`ETA:         ~${Math.ceil((CAPS.length * N * 42 + CAPS.length * 5) / 60)} min`);
  console.log(`Output:      ${OUT_PATH}`);
  console.log(`COMFY_URL:   ${COMFY_URL}`);
  console.log(`Initial cap: ${readCurrentCap()} W`);
  if (DRY_RUN) console.log(`DRY-RUN: cap changes will be skipped`);
  console.log("");

  await preflight();
  sudoAuthenticate();

  for (const sig of ["SIGINT", "SIGTERM"] as const) {
    process.on(sig, () => {
      void gracefulExit(`received ${sig}`, 130);
    });
  }

  csvHandle = await openCsv();

  let runCounter = 0;
  const totalRuns = CAPS.length * N;

  for (const cap of CAPS) {
    console.log(`\n--- Cap = ${cap} W ---`);
    setPowerCap(cap);
    await new Promise((r) => setTimeout(r, SETTLE_MS));

    for (let i = 1; i <= N; i++) {
      runCounter++;
      const t0 = Date.now();
      const row = await runOne(cap, i);
      rows.push(row);
      await csvHandle.append(rowToCsv(row));

      const wallMs = Date.now() - t0;
      const tag = row.error ? `ERROR(${row.error})` : "ok";
      console.log(
        `[${runCounter}/${totalRuns}] cap=${cap}W run=${i}/${N}  render=${(row.render_ms / 1000).toFixed(2)}s  ` +
          `peak=${row.gpu0_power_peak_w.toFixed(0)}W  avg=${row.gpu0_power_avg_w.toFixed(0)}W  ` +
          `t_start=${row.gpu0_temp_start_c}°C t_peak=${row.gpu0_temp_peak_c}°C  ` +
          `wall=${(wallMs / 1000).toFixed(1)}s  ${tag}`,
      );

      if (i < N) await new Promise((r) => setTimeout(r, GAP_MS));
    }
  }

  await gracefulExit("sweep complete", 0);
}

main().catch(async (e) => {
  console.error(`FATAL: ${(e as Error).message}`);
  await gracefulExit("fatal error", 1);
});
