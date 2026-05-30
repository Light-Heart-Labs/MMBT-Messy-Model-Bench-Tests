#!/usr/bin/env python3
"""bench_dashboard_enriched — enriched visual status for the bench autopilot.

Superset of bench_dashboard.py. Reads /tmp/bench-autopilot/status.json + per-cell
grade.json and renders the same color-coded grid (tasks x replicates per arm), plus
five enrichments:

  1) --oneline      : one compact status line (pct, cells, current, endpoint, eta)
  2) baseline delta : per-arm pass-rate vs the N=10 no-think baseline (82/120),
                      with per-task deltas where data exists
  3) sparkline      : ascii completion-over-time, derived from cell summary.json mtimes
  4) events feed    : tail (~8 lines) of /tmp/bench-autopilot/autopilot.log under the grid
  5) robustness     : never crashes on missing/partial status.json — degrades gracefully

The status.json schema + the original CLI (--html/--watch/--no-color) are preserved;
only new flags (--oneline, --no-events, --no-sparkline) and rendering are added.

Usage:
  python3 bench_dashboard_enriched.py             # one-shot terminal render
  python3 bench_dashboard_enriched.py --oneline   # single status line
  python3 bench_dashboard_enriched.py --watch
  python3 bench_dashboard_enriched.py --html /tmp/bench-autopilot/dashboard.html
"""
from __future__ import annotations
import argparse, json, os, time
from pathlib import Path

HOME = Path(os.path.expanduser("~"))
LOGS = HOME / "bench" / "logs"
STATE = Path("/tmp/bench-autopilot")
STATUS = STATE / "status.json"
LOG = STATE / "autopilot.log"

# Glob that matches a cell dir for any arm/rep (e.g. p1_bugfix_397b-nothink_v3).
CELL_GLOB = "p*_397b-*_v*"

# N=10 no-think baseline pass counts per task (totals to 82/120). Used for the
# pass-rate delta enrichment. These are the published Phase-A N=10 numbers; if a
# task is absent here we simply omit its delta.
BASELINE_N10_NOTHINK = {
    "p1_bugfix": 7, "p1_testwrite": 8, "p1_refactor": 6,
    "p2_extract": 7, "p2_ci": 5, "p2_hallucination": 6, "p2_triage": 7,
    "p3_doc": 8, "p3_business": 7, "p3_market": 7, "p3_writing": 7, "p3_pm": 7,
}
BASELINE_N10_TOTAL_PASS = 82
BASELINE_N10_TOTAL_CELLS = 120
# The baseline is the no-think arm; we recognize it by substring so a relabel
# (e.g. "397b-nothink") still matches.
BASELINE_ARM_HINT = "nothink"

C = {"reset":"\033[0m","grn":"\033[42m\033[30m","red":"\033[41m\033[37m",
     "yel":"\033[43m\033[30m","blu":"\033[44m\033[37m","gry":"\033[100m\033[37m",
     "b":"\033[1m","dim":"\033[2m","cyan":"\033[96m","fg_grn":"\033[92m",
     "fg_red":"\033[91m","fg_yel":"\033[93m"}

STATUS_TASKS = []


# ---------------------------------------------------------------------------
# small helpers (all defensive — return safe defaults rather than raising)
# ---------------------------------------------------------------------------
def _g(d, key, default=None):
    """Dict-get that tolerates non-dicts."""
    if isinstance(d, dict):
        return d.get(key, default)
    return default


def verdict(run):
    g = LOGS / run / "grade.json"
    s = LOGS / run / "summary.json"
    try:
        if g.exists():
            try:
                v = json.loads(g.read_text()).get("verdict")
                if v in ("PASS","STRUCTURAL_PASS"): return "pass"
                if v in (None,"BAD_GRADE","GRADER_FAILED","MISSING_OUTPUT"): return "err"
                return "fail"
            except Exception: return "err"
        if s.exists(): return "ungraded"
        if (LOGS / run / "transcript.jsonl").exists(): return "running"
    except Exception:
        return "pending"
    return "pending"


CELL = {"pass":("grn","✓"),"fail":("red","✗"),"err":("yel","!"),
        "ungraded":("blu","·"),"running":("cyan","▶"),"pending":("gry"," ")}


def render_grid(arm, target, color=True):
    label = _g(arm, "label", "?"); tasks = _g(arm, "pertask", {}) or {}
    lines = []
    head = "  " + "".join(f"{v:>3}" for v in range(1,target+1))
    lines.append(f"{C['b'] if color else ''}{label}{C['reset'] if color else ''}   {C['dim'] if color else ''}{head}{C['reset'] if color else ''}")
    for t in STATUS_TASKS:
        row = f"{t:<17}"
        for v in range(1,target+1):
            st = verdict(f"{t}_{label}_v{v}")
            ck, ch = CELL[st]
            if color:
                row += f" {C[ck]}{ch}{C['reset']} "
            else:
                row += f" {ch} "
        pt = tasks.get(t,{}) if isinstance(tasks, dict) else {}
        row += f"  {_g(pt,'pass','?')}/{_g(pt,'done','?')}"
        # baseline delta (enrichment #2) appended per task where data exists
        if BASELINE_ARM_HINT in str(label):
            base = BASELINE_N10_NOTHINK.get(t)
            if base is not None and isinstance(pt, dict) and isinstance(pt.get("pass"), int):
                d = pt["pass"] - base
                sign = "+" if d > 0 else ("" if d == 0 else "")
                col = (C['fg_grn'] if d > 0 else C['fg_red'] if d < 0 else C['dim']) if color else ""
                rs = C['reset'] if color else ""
                row += f"  {col}{sign}{d:>+d} vs {base}/10{rs}"
        lines.append(row)
    return "\n".join(lines)


def _cell_summaries():
    """All cell summary.json paths sorted by mtime (oldest first). Safe on errors."""
    try:
        sums = list(LOGS.glob(f"{CELL_GLOB}/summary.json"))
        sums.sort(key=lambda p: p.stat().st_mtime)
        return sums
    except Exception:
        return []


def human_eta(status):
    try:
        done = _g(status, "grand_done", 0) or 0
        total = _g(status, "grand_total", 0) or 0
        rem = total - done
        sums = _cell_summaries()[-9:]
        if len(sums) >= 2:
            span = sums[-1].stat().st_mtime - sums[0].stat().st_mtime
            per = span / (len(sums)-1)
            if per <= 0:
                return "n/a"
            secs = int(rem * per)
            h, m = secs//3600, (secs%3600)//60
            return f"~{h}h{m:02d}m (≈{per/60:.1f}min/cell over last {len(sums)} cells)"
    except Exception:
        pass
    return "n/a"


# ---------------------------------------------------------------------------
# enrichment #3 — completion sparkline over time (from summary.json mtimes)
# ---------------------------------------------------------------------------
SPARK = "▁▂▃▄▅▆▇█"

def completion_sparkline(buckets=24, window_secs=None):
    """Bin cell-completion times into `buckets` equal slots over the run's span
    and render an ascii block sparkline of cells-completed-per-bin."""
    try:
        sums = _cell_summaries()
        if len(sums) < 2:
            return None, 0
        mts = [p.stat().st_mtime for p in sums]
        t0, t1 = mts[0], mts[-1]
        if window_secs:
            t0 = max(t0, t1 - window_secs)
            mts = [m for m in mts if m >= t0]
            if len(mts) < 2:
                return None, 0
        span = max(t1 - t0, 1e-6)
        counts = [0] * buckets
        for m in mts:
            idx = min(buckets - 1, int((m - t0) / span * buckets))
            counts[idx] += 1
        peak = max(counts) or 1
        spark = "".join(SPARK[min(len(SPARK)-1, int(c / peak * (len(SPARK)-1)))] for c in counts)
        mins = int(span / 60)
        return f"{spark}  ({len(mts)} cells over ~{mins}m, peak {peak}/bin)", len(mts)
    except Exception:
        return None, 0


# ---------------------------------------------------------------------------
# enrichment #4 — recent-events feed (tail of autopilot.log)
# ---------------------------------------------------------------------------
def recent_events(n=8):
    try:
        if not LOG.exists():
            return []
        # tail without loading huge files entirely
        data = LOG.read_text(errors="replace").splitlines()
        return data[-n:]
    except Exception:
        return []


# ---------------------------------------------------------------------------
# enrichment #2 — per-arm pass-rate vs baseline (summary line)
# ---------------------------------------------------------------------------
def arm_baseline_line(arm, color=True):
    label = _g(arm, "label", "?")
    pertask = _g(arm, "pertask", {}) or {}
    if not isinstance(pertask, dict):
        return None
    if BASELINE_ARM_HINT not in str(label):
        return None
    cur_pass = sum(_g(p, "pass", 0) or 0 for p in pertask.values() if isinstance(p, dict))
    cur_done = sum(_g(p, "done", 0) or 0 for p in pertask.values() if isinstance(p, dict))
    if cur_done == 0:
        return None
    cur_rate = cur_pass / cur_done
    base_rate = BASELINE_N10_TOTAL_PASS / BASELINE_N10_TOTAL_CELLS
    d = (cur_rate - base_rate) * 100
    col = (C['fg_grn'] if d >= 0 else C['fg_red']) if color else ""
    rs = C['reset'] if color else ""
    return (f"    {label} pass-rate: {cur_pass}/{cur_done} = {cur_rate*100:.1f}%   "
            f"baseline N=10 {BASELINE_N10_TOTAL_PASS}/{BASELINE_N10_TOTAL_CELLS} = {base_rate*100:.1f}%   "
            f"{col}Δ {d:+.1f}pp{rs}")


# ---------------------------------------------------------------------------
# enrichment #1 — oneline
# ---------------------------------------------------------------------------
def oneline(status, color=True):
    if status is None:
        return "bench: no status.json yet (autopilot not started?)"
    pct = _g(status, "pct", "?")
    gd = _g(status, "grand_done", "?"); gt = _g(status, "grand_total", "?")
    cur = _g(status, "current", {}) or {}
    up = _g(status, "endpoint_up", None)
    phase = _g(status, "phase", "?")
    if color:
        ep = (C['fg_grn']+"UP"+C['reset']) if up else (C['fg_red']+"DOWN"+C['reset'] if up is not None else "?")
    else:
        ep = "UP" if up else ("DOWN" if up is not None else "?")
    eta = human_eta(status)
    cell = _g(cur, "cell", "-") or "-"
    return (f"MMBT {phase} {pct}% [{gd}/{gt}]  ep={ep}  "
            f"cur={cell} iter={_g(cur,'iter','-')} frozen={_g(cur,'frozen_secs','-')}s  ETA {eta}")


# ---------------------------------------------------------------------------
# full terminal render
# ---------------------------------------------------------------------------
def render(status, color=True, show_events=True, show_spark=True):
    global STATUS_TASKS
    if status is None:
        return "no status yet (autopilot not started?)"
    STATUS_TASKS = _g(status, "tasks", []) or []
    L = []
    rs = C["reset"] if color else ""
    bar_w = 40
    pct = _g(status, "pct", 0) or 0
    filled = int(bar_w * pct/100)
    bar = "█"*filled + "░"*(bar_w-filled)
    up = _g(status, "endpoint_up", None)
    hp = "UP" if up else ("DOWN" if up is not None else "?")
    hcol = C["grn"] if (up and color) else (C["red"] if (up is not None and color) else "")
    L.append(f"{C['b'] if color else ''}MMBT bench autopilot — N={_g(status,'target_n','?')} — {_g(status,'phase','?')}{rs}")
    L.append(f"  {bar} {pct}%  ({_g(status,'grand_done','?')}/{_g(status,'grand_total','?')} cells)")
    cur = _g(status, "current", {}) or {}
    L.append(f"  endpoint: {hcol}{hp}{rs}   current: {C['cyan'] if color else ''}{_g(cur,'cell','-')}{rs} iter={_g(cur,'iter','-')} frozen={_g(cur,'frozen_secs','-')}s")
    L.append(f"  ETA: {human_eta(status)}   updated: {_g(status,'updated','?')}")
    if show_spark:
        spark, _ = completion_sparkline()
        if spark:
            L.append(f"  pace: {C['cyan'] if color else ''}{spark}{rs}")
    L.append("")
    arms = _g(status, "arms", []) or []
    for arm in arms:
        L.append(render_grid(arm, _g(status,'target_n',0) or 0, color))
        pertask = _g(arm, "pertask", {}) or {}
        subtotal = sum(_g(p,'pass',0) or 0 for p in pertask.values() if isinstance(p, dict))
        L.append(f"    {_g(arm,'label','?')} subtotal: {subtotal}/{_g(arm,'done','?')} pass  ({_g(arm,'done','?')}/{_g(arm,'total','?')} cells)")
        bl = arm_baseline_line(arm, color)
        if bl:
            L.append(bl)
        L.append("")
    if color:
        L.append(f"  legend: {C['grn']}✓{rs}pass {C['red']}✗{rs}fail {C['yel']}!{rs}grader {C['blu']}·{rs}ungraded {C['cyan']}▶{rs}running {C['gry']} {rs}pending")
    if show_events:
        ev = recent_events(8)
        if ev:
            L.append("")
            L.append(f"  {C['b'] if color else ''}recent events{rs} ({LOG}):")
            for line in ev:
                L.append(f"  {C['dim'] if color else ''}{line}{rs}")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# HTML render (preserves original layout, adds spark + baseline + events)
# ---------------------------------------------------------------------------
def to_html(status):
    if status is None:
        return ("<!doctype html><meta http-equiv=refresh content=15>"
                "<body style='background:#111;color:#ddd;font-family:system-ui'>"
                "<h2>MMBT bench autopilot</h2><p>no status.json yet "
                "(autopilot not started?)</p></body>")
    tasks_local = _g(status, "tasks", []) or []
    target_n = _g(status, "target_n", 0) or 0
    hc = {"pass":"#1a7f37","fail":"#b91c1c","err":"#b8860b","ungraded":"#1f5fbf","running":"#0aa","pending":"#444"}
    rows = []
    for arm in (_g(status, "arms", []) or []):
        label = _g(arm, "label", "?")
        pertask = _g(arm, "pertask", {}) or {}
        subtotal = sum(_g(p,'pass',0) or 0 for p in pertask.values() if isinstance(p, dict))
        bl = arm_baseline_line(arm, color=False)
        bl_html = f"<div style='color:#9cf;font:12px monospace'>{bl.strip()}</div>" if bl else ""
        rows.append(f"<h3>{label} — {subtotal}/{_g(arm,'done','?')} pass ({_g(arm,'done','?')}/{_g(arm,'total','?')})</h3>{bl_html}<table style='border-collapse:collapse'>")
        hdr = "<tr><th></th>" + "".join(f"<th style='font:11px monospace;color:#888'>{v}</th>" for v in range(1,target_n+1)) + "<th>p/d</th><th>Δ</th></tr>"
        rows.append(hdr)
        for t in tasks_local:
            cells = ""
            for v in range(1,target_n+1):
                st = verdict(f"{t}_{label}_v{v}")
                cells += f"<td title='{t}_v{v}:{st}' style='width:16px;height:16px;background:{hc[st]}'></td>"
            pt = pertask.get(t,{}) if isinstance(pertask, dict) else {}
            delta = ""
            if BASELINE_ARM_HINT in str(label):
                base = BASELINE_N10_NOTHINK.get(t)
                if base is not None and isinstance(_g(pt,"pass"), int):
                    d = pt["pass"] - base
                    dcol = "#5fd35f" if d > 0 else "#e06666" if d < 0 else "#888"
                    delta = f"<span style='color:{dcol}'>{d:+d} vs {base}/10</span>"
            rows.append(f"<tr><td style='font:12px monospace;padding-right:6px'>{t}</td>{cells}<td style='font:11px monospace;color:#aaa'>{_g(pt,'pass','?')}/{_g(pt,'done','?')}</td><td style='font:11px monospace'>{delta}</td></tr>")
        rows.append("</table>")
    spark, _ = completion_sparkline()
    spark_html = f"<p style='font:14px monospace;color:#9cf'>pace: {spark}</p>" if spark else ""
    ev = recent_events(8)
    ev_html = ""
    if ev:
        body = "<br>".join(_html_escape(x) for x in ev)
        ev_html = f"<h3>recent events</h3><pre style='background:#000;color:#9c9;padding:8px;font:12px monospace;white-space:pre-wrap'>{body}</pre>"
    cur = _g(status, "current", {}) or {}
    return f"""<!doctype html><meta http-equiv=refresh content=30><body style='background:#111;color:#ddd;font-family:system-ui'>
<h2>MMBT bench autopilot — N={target_n} — {_g(status,'phase','?')} — {_g(status,'pct','?')}%</h2>
<p>{_g(status,'grand_done','?')}/{_g(status,'grand_total','?')} cells · endpoint {'UP' if _g(status,'endpoint_up') else 'DOWN'} · current {_g(cur,'cell','-')} iter {_g(cur,'iter','-')} · updated {_g(status,'updated','?')}</p>
{spark_html}
{''.join(rows)}
<p style='color:#888'>green=pass red=fail yellow=grader-issue blue=ungraded teal=running grey=pending</p>
{ev_html}
</body>"""


def _html_escape(s):
    return (str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"))


# ---------------------------------------------------------------------------
def load_status():
    """Load status.json, tolerating missing/partial/corrupt files. Returns dict or None."""
    try:
        if not STATUS.exists():
            return None
        txt = STATUS.read_text()
        if not txt.strip():
            return None
        return json.loads(txt)
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--watch", action="store_true")
    ap.add_argument("--html", default=None)
    ap.add_argument("--no-color", action="store_true")
    ap.add_argument("--oneline", action="store_true", help="single compact status line")
    ap.add_argument("--no-events", action="store_true", help="hide the recent-events feed")
    ap.add_argument("--no-sparkline", action="store_true", help="hide the completion sparkline")
    args = ap.parse_args()

    def once():
        status = load_status()  # None if missing/partial — every renderer handles None
        if args.oneline:
            print(oneline(status, color=not args.no_color))
            return
        if args.html:
            try:
                Path(args.html).write_text(to_html(status))
                print(f"wrote {args.html}")
            except Exception as e:
                print(f"failed to write {args.html}: {e}")
            return
        out = render(status, color=not args.no_color,
                     show_events=not args.no_events, show_spark=not args.no_sparkline)
        if args.watch:
            os.system("clear")
        print(out)

    if args.watch:
        while True:
            try:
                once()
            except Exception as e:
                # last-resort guard: a render error must never kill the watch loop
                print(f"[dashboard] transient render error: {e}")
            time.sleep(15)
    else:
        once()


if __name__ == "__main__":
    main()
