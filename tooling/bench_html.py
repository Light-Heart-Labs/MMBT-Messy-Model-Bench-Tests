#!/usr/bin/env python3
"""bench_html.py — rich, auto-refreshing HTML dashboard for the MMBT microbench.

STANDALONE read-only generator. Reads (all optional / partial-tolerant):
  * /tmp/bench-autopilot/status.json          — header, arms, pertask, current cell, pct
  * ~/bench/logs/<run_name>/grade.json         — per-cell verdict (top-level "verdict")
  * ~/bench/logs/<run_name>/summary.json       — cell-done marker + mtime (pace/ETA)
  * /tmp/bench-autopilot/autopilot.log          — recent events feed (falls back to
                                                   nohup.log / run-*.log if absent)

Writes a single self-contained HTML file (default
/tmp/bench-autopilot/dashboard.html) carrying <meta http-equiv=refresh content=20>,
a mobile-friendly dark theme, and:
  - header: pct progress bar, endpoint/container health, current cell + iter +
    frozen, ETA, last-updated
  - full tasks x reps grid per arm with colored cells
      pass=green fail=red grader-issue=amber ungraded=blue running=teal pending=grey
      each cell carries a hover title = "<run_name> — <verdict>"
  - per-task N=10 no-think baseline delta column (on the no-think arm)
  - completion sparkline (cells/time bucket)
  - compact think-vs-no-think per-task pass-rate comparison table
  - recent autopilot.log events

Design rule: NEVER crash on missing/partial/garbage data — every reader is
defensive and returns a safe default. The live N=20 run's files are only ever
READ here; nothing is mutated.

Usage:
  python3 bench_html.py                 # write default dashboard.html once
  python3 bench_html.py --out FILE      # custom output path
  python3 bench_html.py --refresh 30    # custom meta-refresh seconds (0 = none)
  python3 bench_html.py --watch         # re-render every --interval seconds
  python3 bench_html.py --interval 15   # watch loop period
  python3 bench_html.py --stdout        # also print HTML to stdout
"""
from __future__ import annotations
import argparse, html, json, os, statistics, time
from pathlib import Path

HOME = Path(os.path.expanduser("~"))
LOGS = HOME / "bench" / "logs"
STATE = Path("/tmp/bench-autopilot")
STATUS = STATE / "status.json"
LOG = STATE / "autopilot.log"
# Fallback event sources if autopilot.log has not been created yet.
LOG_FALLBACKS = [STATE / "nohup.log"]

DEFAULT_OUT = STATE / "dashboard.html"

TASKS = ["p1_bugfix", "p1_testwrite", "p1_refactor", "p2_extract", "p2_ci",
         "p2_hallucination", "p2_triage", "p3_doc", "p3_business", "p3_market",
         "p3_writing", "p3_pm"]

# N=10 no-think per-task pass baseline (sums to 82/120) — published Phase-A nums.
BASELINE_N10_NOTHINK = {
    "p1_bugfix": 10, "p1_testwrite": 0, "p1_refactor": 0,
    "p2_extract": 10, "p2_ci": 10, "p2_hallucination": 10, "p2_triage": 10,
    "p3_doc": 9, "p3_business": 10, "p3_market": 8, "p3_writing": 0, "p3_pm": 5,
}
BASELINE_N10_TOTAL_PASS = 82
BASELINE_N10_TOTAL_CELLS = 120
BASELINE_ARM_HINT = "nothink"

PASS_VERDICTS = ("PASS", "STRUCTURAL_PASS")
GRADER_VERDICTS = (None, "BAD_GRADE", "GRADER_FAILED", "MISSING_OUTPUT")

# cell-state -> (css class, glyph, label)
STATE_META = {
    "pass":     ("c-pass", "✓", "pass"),
    "fail":     ("c-fail", "✗", "fail"),
    "err":      ("c-err",  "!",      "grader-issue"),
    "ungraded": ("c-ung",  "·", "ungraded"),
    "running":  ("c-run",  "▶", "running"),
    "pending":  ("c-pend", "",       "pending"),
}
SPARK = "▁▂▃▄▅▆▇█"


# --------------------------------------------------------------------------- #
# defensive readers
# --------------------------------------------------------------------------- #
def _g(d, key, default=None):
    return d.get(key, default) if isinstance(d, dict) else default


def load_status():
    try:
        if STATUS.exists():
            return json.loads(STATUS.read_text(errors="replace"))
    except Exception:
        pass
    return None


def raw_verdict(run_name):
    """Top-level grade.json verdict string, or None if missing/unparseable."""
    g = LOGS / run_name / "grade.json"
    try:
        if g.exists():
            return json.loads(g.read_text(errors="replace")).get("verdict")
    except Exception:
        return None
    return None


def cell_state(run_name):
    """Map a cell to one of the STATE_META keys (mirrors bench_dashboard.verdict)."""
    d = LOGS / run_name
    try:
        g = d / "grade.json"
        if g.exists():
            try:
                v = json.loads(g.read_text(errors="replace")).get("verdict")
            except Exception:
                return "err"
            if v in PASS_VERDICTS:
                return "pass"
            if v in GRADER_VERDICTS:
                return "err"
            return "fail"
        if (d / "summary.json").exists():
            return "ungraded"
        if (d / "transcript.jsonl").exists():
            return "running"
    except Exception:
        return "pending"
    return "pending"


def cell_title(run_name):
    v = raw_verdict(run_name)
    return f"{run_name} — {v if v is not None else 'ungraded/pending'}"


def _arm_label_glob(status):
    """Shared prefix of arm labels for cell-dir globbing (defensive)."""
    arms = _g(status, "arms", []) or []
    labels = [_g(a, "label") for a in arms if _g(a, "label")]
    if not labels:
        return "397b-"
    s1, s2 = min(labels), max(labels)
    i = 0
    while i < len(s1) and i < len(s2) and s1[i] == s2[i]:
        i += 1
    return s1[:i] or labels[0]


def _cell_summaries(status):
    try:
        frag = _arm_label_glob(status)
        sums = list(LOGS.glob(f"p*_{frag}*_v*/summary.json"))
        sums.sort(key=lambda p: p.stat().st_mtime)
        return sums
    except Exception:
        return []


def human_eta(status):
    try:
        done = _g(status, "grand_done", 0) or 0
        total = _g(status, "grand_total", 0) or 0
        rem = max(total - done, 0)
        sums = _cell_summaries(status)[-9:]
        if len(sums) >= 2:
            span = sums[-1].stat().st_mtime - sums[0].stat().st_mtime
            per = span / (len(sums) - 1)
            if per <= 0:
                return "n/a"
            secs = int(rem * per)
            h, m = secs // 3600, (secs % 3600) // 60
            return f"~{h}h{m:02d}m ({per/60:.1f} min/cell, last {len(sums)})"
    except Exception:
        pass
    return "n/a"


def completion_sparkline(status, buckets=30):
    try:
        sums = _cell_summaries(status)
        if len(sums) < 2:
            return None
        mts = [p.stat().st_mtime for p in sums]
        t0, t1 = mts[0], mts[-1]
        span = max(t1 - t0, 1e-6)
        counts = [0] * buckets
        for m in mts:
            idx = min(buckets - 1, int((m - t0) / span * buckets))
            counts[idx] += 1
        peak = max(counts) or 1
        spark = "".join(
            SPARK[min(len(SPARK) - 1, int(c / peak * (len(SPARK) - 1)))] for c in counts
        )
        mins = int(span / 60)
        return f"{spark}", f"{len(mts)} cells over ~{mins}m, peak {peak}/bin"
    except Exception:
        return None


def recent_events(n=12):
    src = LOG if LOG.exists() else None
    if src is None:
        for fb in LOG_FALLBACKS:
            if fb.exists():
                src = fb
                break
    if src is None:
        return [], None
    try:
        data = src.read_text(errors="replace").splitlines()
        return [ln for ln in data[-n:] if ln.strip()], src
    except Exception:
        return [], src


# --------------------------------------------------------------------------- #
# html building
# --------------------------------------------------------------------------- #
def esc(x):
    return html.escape("" if x is None else str(x), quote=True)


def header_html(status):
    pct = _g(status, "pct", 0) or 0
    try:
        pct = float(pct)
    except Exception:
        pct = 0.0
    gd = _g(status, "grand_done", "?")
    gt = _g(status, "grand_total", "?")
    cur = _g(status, "current", {}) or {}
    up = _g(status, "endpoint_up", None)
    cu = _g(status, "container_up", None)

    def badge(val, up_txt="UP", down_txt="DOWN"):
        if val is True:
            return f"<span class='b b-up'>{up_txt}</span>"
        if val is False:
            return f"<span class='b b-down'>{down_txt}</span>"
        return "<span class='b b-unk'>?</span>"

    eta = esc(human_eta(status))
    phase = esc(_g(status, "phase", "?"))
    tn = esc(_g(status, "target_n", "?"))
    cell = esc(_g(cur, "cell", "-") or "-")
    it = esc(_g(cur, "iter", "-"))
    fz = esc(_g(cur, "frozen_secs", "-"))
    upd = esc(_g(status, "updated", "?"))

    spk = completion_sparkline(status)
    spark_html = ""
    if spk:
        spark_html = (f"<div class='spark'><span class='sline'>{esc(spk[0])}</span>"
                      f"<span class='smeta'>{esc(spk[1])}</span></div>")

    return f"""
<header>
  <div class='htop'>
    <div class='title'>MMBT bench autopilot &mdash; N={tn} &mdash; <span class='phase'>{phase}</span></div>
    <div class='upd'>updated {upd}</div>
  </div>
  <div class='barwrap' title='{esc(pct)}%'>
    <div class='bar' style='width:{max(0.0,min(100.0,pct)):.1f}%'></div>
    <div class='bartext'>{esc(round(pct,1))}% &nbsp; ({gd}/{gt} cells)</div>
  </div>
  <div class='hmeta'>
    <span>endpoint {badge(up)}</span>
    <span>container {badge(cu)}</span>
    <span>current <code>{cell}</code></span>
    <span>iter <b>{it}</b></span>
    <span>frozen <b>{fz}s</b></span>
    <span>ETA <b>{eta}</b></span>
  </div>
  {spark_html}
</header>
"""


def grid_html(arm, target):
    label = _g(arm, "label", "?")
    pertask = _g(arm, "pertask", {}) or {}
    is_base_arm = BASELINE_ARM_HINT in str(label)
    try:
        target = int(target)
    except Exception:
        target = 0

    head_cells = "".join(f"<th class='rep'>{v}</th>" for v in range(1, target + 1))
    base_h = "<th class='delta'>vs N=10</th>" if is_base_arm else ""
    rows = []
    for t in TASKS:
        cells = []
        for v in range(1, target + 1):
            rn = f"{t}_{label}_v{v}"
            st = cell_state(rn)
            cls, glyph, _lab = STATE_META.get(st, STATE_META["pending"])
            cells.append(f"<td class='cell {cls}' title='{esc(cell_title(rn))}'>{glyph}</td>")
        pt = pertask.get(t, {}) if isinstance(pertask, dict) else {}
        p = _g(pt, "pass", "?")
        dn = _g(pt, "done", "?")
        delta_cell = ""
        if is_base_arm:
            base = BASELINE_N10_NOTHINK.get(t)
            if base is not None and isinstance(p, int):
                d = p - base
                dcls = "d-pos" if d > 0 else ("d-neg" if d < 0 else "d-zero")
                delta_cell = f"<td class='delta {dcls}'>{d:+d} <span class='dim'>/ {base}</span></td>"
            else:
                delta_cell = "<td class='delta d-zero'>&mdash;</td>"
        rows.append(
            f"<tr><th class='taskname'>{esc(t)}</th>{''.join(cells)}"
            f"<td class='pn'>{esc(p)}/{esc(dn)}</td>{delta_cell}</tr>"
        )

    done = _g(arm, "done", "?")
    total = _g(arm, "total", "?")
    subtotal = sum(_g(p, "pass", 0) or 0 for p in pertask.values() if isinstance(p, dict))
    sub_done = sum(_g(p, "done", 0) or 0 for p in pertask.values() if isinstance(p, dict))
    base_line = ""
    if is_base_arm and sub_done:
        cur_rate = subtotal / sub_done * 100
        base_rate = BASELINE_N10_TOTAL_PASS / BASELINE_N10_TOTAL_CELLS * 100
        dpp = cur_rate - base_rate
        dcls = "d-pos" if dpp >= 0 else "d-neg"
        base_line = (f"<span class='blinfo'>pass-rate {subtotal}/{sub_done} = {cur_rate:.1f}% "
                     f"&middot; baseline 82/120 = {base_rate:.1f}% "
                     f"&middot; <span class='{dcls}'>Δ {dpp:+.1f}pp</span></span>")

    return f"""
<section class='armblock'>
  <div class='armhdr'>
    <span class='armlabel'>{esc(label)}</span>
    <span class='armsub'>subtotal {subtotal}/{esc(done)} pass &middot; {esc(done)}/{esc(total)} cells</span>
    {base_line}
  </div>
  <div class='gridscroll'>
    <table class='grid'>
      <thead><tr><th class='taskname'>task</th>{head_cells}<th class='pn'>p/n</th>{base_h}</tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </div>
</section>
"""


def compare_html(status):
    """Compact think-vs-no-think per-task pass-rate comparison table."""
    arms = _g(status, "arms", []) or []
    nothink = next((a for a in arms if "nothink" in str(_g(a, "label", "")).lower()), None)
    # think arm: has 'think' but not 'nothink'
    think = next((a for a in arms
                  if "think" in str(_g(a, "label", "")).lower()
                  and "nothink" not in str(_g(a, "label", "")).lower()), None)
    if nothink is None and think is None:
        return ""

    def rate(arm, t):
        pt = (_g(arm, "pertask", {}) or {}).get(t, {}) if arm else {}
        p = _g(pt, "pass", None)
        dn = _g(pt, "done", None)
        if isinstance(p, int) and isinstance(dn, int) and dn > 0:
            return p, dn, p / dn * 100
        if isinstance(dn, int) and dn == 0:
            return 0, 0, None
        return None, None, None

    def cellfmt(r):
        p, dn, pct = r
        if pct is None:
            return "<td class='cmp dim'>&mdash;</td>"
        cls = "cmp-hi" if pct >= 75 else ("cmp-mid" if pct >= 40 else "cmp-lo")
        return f"<td class='cmp {cls}'>{p}/{dn}<br><small>{pct:.0f}%</small></td>"

    rows = []
    for t in TASKS:
        rn = rate(nothink, t)
        rt = rate(think, t)
        # bar of which arm leads (only if both have data)
        lead = ""
        if rn[2] is not None and rt[2] is not None:
            if rn[2] > rt[2]:
                lead = "<span class='lead lead-n'>no-think</span>"
            elif rt[2] > rn[2]:
                lead = "<span class='lead lead-t'>think</span>"
            else:
                lead = "<span class='lead lead-e'>tie</span>"
        rows.append(f"<tr><th class='taskname'>{esc(t)}</th>{cellfmt(rn)}{cellfmt(rt)}<td class='leadcol'>{lead}</td></tr>")

    nlabel = esc(_g(nothink, "label", "no-think")) if nothink else "no-think"
    tlabel = esc(_g(think, "label", "think")) if think else "think"
    return f"""
<section class='cmpblock'>
  <h3>think vs no-think &mdash; per-task pass rate</h3>
  <div class='gridscroll'>
    <table class='cmptbl'>
      <thead><tr><th class='taskname'>task</th><th>{nlabel}</th><th>{tlabel}</th><th>leads</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </div>
</section>
"""


def events_html():
    ev, src = recent_events(12)
    if not ev:
        return "<section class='evblock'><h3>recent events</h3><pre class='ev'>(no autopilot.log yet)</pre></section>"
    body = "\n".join(esc(line) for line in ev)
    return (f"<section class='evblock'><h3>recent events "
            f"<span class='dim'>({esc(src)})</span></h3><pre class='ev'>{body}</pre></section>")


def legend_html():
    items = []
    for st in ("pass", "fail", "err", "ungraded", "running", "pending"):
        cls, glyph, lab = STATE_META[st]
        g = glyph or "&nbsp;"
        items.append(f"<span class='lg'><span class='cell {cls} lgcell'>{g}</span>{lab}</span>")
    return "<div class='legend'>" + " ".join(items) + "</div>"


CSS = """
:root{--bg:#0d1117;--panel:#161b22;--panel2:#1c2430;--fg:#e6edf3;--dim:#8b949e;
--line:#30363d;--accent:#2f81f7;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
font-size:14px;line-height:1.4;padding:10px;-webkit-text-size-adjust:100%}
code,pre,.sline{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
header{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin-bottom:14px}
.htop{display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:6px}
.title{font-weight:700;font-size:16px}
.phase{color:var(--accent)}
.upd{color:var(--dim);font-size:12px}
.barwrap{position:relative;height:22px;background:var(--panel2);border-radius:6px;margin:10px 0;overflow:hidden;border:1px solid var(--line)}
.bar{position:absolute;top:0;left:0;height:100%;background:linear-gradient(90deg,#1f6feb,#2ea043);transition:width .4s}
.bartext{position:absolute;width:100%;text-align:center;line-height:22px;font-size:12px;font-weight:600;text-shadow:0 1px 2px #000}
.hmeta{display:flex;flex-wrap:wrap;gap:6px 16px;color:var(--dim);font-size:13px}
.hmeta b{color:var(--fg)}
.hmeta code{color:#79c0ff;background:var(--panel2);padding:1px 5px;border-radius:4px}
.b{padding:1px 7px;border-radius:10px;font-size:11px;font-weight:700}
.b-up{background:#12361f;color:#3fb950}.b-down{background:#3d1418;color:#f85149}.b-unk{background:#30363d;color:#8b949e}
.spark{margin-top:8px;color:var(--dim);font-size:12px}
.sline{font-size:16px;letter-spacing:1px;color:#58a6ff}
.smeta{margin-left:8px}
section{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:10px 12px;margin-bottom:14px}
.armhdr{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 14px;margin-bottom:8px}
.armlabel{font-weight:700;font-size:15px;color:#ffa657}
.armsub{color:var(--dim);font-size:12px}
.blinfo{color:var(--dim);font-size:12px}
.gridscroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
table{border-collapse:collapse;width:100%}
.grid th,.grid td{text-align:center;font-size:12px;padding:0}
.grid thead th{color:var(--dim);font-weight:600;padding:2px 3px}
.taskname{text-align:left!important;color:var(--fg);white-space:nowrap;padding-right:8px!important;font-weight:600;position:sticky;left:0;background:var(--panel);z-index:1}
.rep{min-width:18px}
.cell{width:20px;height:20px;border:1px solid #0d1117;color:#fff;font-weight:700;line-height:20px;border-radius:3px}
.c-pass{background:#1a7f37}.c-fail{background:#b62324}.c-err{background:#b8860b;color:#1d1d1d}
.c-ung{background:#1f5fbf}.c-run{background:#0a8f8f}.c-pend{background:#2a313a;color:#555}
.pn{padding:0 8px!important;color:var(--fg);white-space:nowrap;font-weight:600}
.delta{padding:0 6px!important;white-space:nowrap;font-weight:700}
.d-pos{color:#3fb950}.d-neg{color:#f85149}.d-zero{color:var(--dim)}
.dim{color:var(--dim)}
.legend{display:flex;flex-wrap:wrap;gap:10px 14px;color:var(--dim);font-size:12px;margin:6px 2px}
.lg{display:inline-flex;align-items:center;gap:5px}
.lgcell{display:inline-block}
.cmptbl th,.cmptbl td{padding:4px 6px;text-align:center;border-bottom:1px solid var(--line);font-size:12px}
.cmptbl thead th{color:var(--dim)}
.cmp-hi{color:#3fb950}.cmp-mid{color:#d29922}.cmp-lo{color:#f85149}
.cmp small{color:var(--dim)}
.lead{padding:1px 6px;border-radius:8px;font-size:11px;font-weight:700}
.lead-n{background:#12361f;color:#3fb950}.lead-t{background:#1c2f4a;color:#58a6ff}.lead-e{background:#30363d;color:#8b949e}
.evblock h3,.cmpblock h3{margin:2px 0 8px;font-size:13px;color:var(--fg)}
.ev{background:#010409;border:1px solid var(--line);border-radius:6px;color:#9ad0a0;
font-size:11.5px;padding:8px;white-space:pre-wrap;word-break:break-word;max-height:260px;overflow:auto;margin:0}
footer{color:var(--dim);font-size:11px;text-align:center;margin:8px 0 18px}
@media(max-width:600px){body{font-size:13px}.cell{width:17px;height:17px;line-height:17px}.title{font-size:15px}}
"""


def build_html(status, refresh=20):
    refresh_tag = (f"<meta http-equiv='refresh' content='{int(refresh)}'>"
                   if refresh and int(refresh) > 0 else "")
    gen_ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    if status is None:
        body = ("<header><div class='title'>MMBT bench autopilot</div></header>"
                "<section><p>no <code>status.json</code> yet "
                "(autopilot not started, or file missing).</p>"
                "<p class='dim'>This page will keep refreshing.</p></section>")
    else:
        target = _g(status, "target_n", 0) or 0
        arms = _g(status, "arms", []) or []
        parts = [header_html(status), legend_html()]
        for arm in arms:
            try:
                parts.append(grid_html(arm, target))
            except Exception as e:
                parts.append(f"<section><p class='dim'>grid render error: {esc(e)}</p></section>")
        try:
            parts.append(compare_html(status))
        except Exception as e:
            parts.append(f"<section><p class='dim'>compare render error: {esc(e)}</p></section>")
        parts.append(events_html())
        body = "".join(parts)

    return (f"<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"{refresh_tag}<title>MMBT bench dashboard</title><style>{CSS}</style></head>"
            f"<body>{body}<footer>generated {esc(gen_ts)} &middot; "
            f"auto-refresh {esc(refresh)}s &middot; bench_html.py</footer></body></html>")


def render_once(out_path, refresh, also_stdout=False):
    status = load_status()
    try:
        doc = build_html(status, refresh=refresh)
    except Exception as e:
        # Last-resort: never produce nothing.
        doc = (f"<!doctype html><meta http-equiv='refresh' content='{int(refresh) if refresh else 20}'>"
               f"<body style='background:#0d1117;color:#e6edf3;font-family:system-ui'>"
               f"<h2>MMBT bench dashboard</h2><p>render error: {esc(e)}</p></body>")
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(doc, encoding="utf-8")
    except Exception as e:
        print(f"write error: {e}")
        return None
    if also_stdout:
        print(doc)
    return out_path


def main():
    ap = argparse.ArgumentParser(description="Rich auto-refreshing HTML dashboard for the MMBT microbench.")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help=f"output HTML path (default {DEFAULT_OUT})")
    ap.add_argument("--refresh", type=int, default=20, help="meta-refresh seconds (0 = none)")
    ap.add_argument("--watch", action="store_true", help="re-render on a loop")
    ap.add_argument("--interval", type=int, default=15, help="watch loop period in seconds")
    ap.add_argument("--stdout", action="store_true", help="also print HTML to stdout")
    args = ap.parse_args()
    out = Path(args.out)

    if args.watch:
        try:
            while True:
                p = render_once(out, args.refresh, also_stdout=False)
                print(f"{time.strftime('%H:%M:%S')} wrote {p}")
                time.sleep(max(1, args.interval))
        except KeyboardInterrupt:
            print("\nstopped.")
    else:
        p = render_once(out, args.refresh, also_stdout=args.stdout)
        if p:
            print(f"wrote {p}")


if __name__ == "__main__":
    main()
