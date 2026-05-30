#!/usr/bin/env python3
"""bench_dashboard — visual status for the bench autopilot.

Reads /tmp/bench-autopilot/status.json + per-cell grade.json and renders a
color-coded grid (tasks x replicates, per reasoning arm) plus progress, health,
current cell, and a rough ETA. Terminal (ANSI) by default; --html writes an HTML
file; --watch refreshes in place.

Usage:
  python3 bench_dashboard.py            # one-shot terminal render
  python3 bench_dashboard.py --watch    # live refresh
  python3 bench_dashboard.py --html /tmp/bench-autopilot/dashboard.html
"""
from __future__ import annotations
import argparse, json, os, time
from pathlib import Path

HOME = Path(os.path.expanduser("~"))
LOGS = HOME / "bench" / "logs"
STATE = Path("/tmp/bench-autopilot")
STATUS = STATE / "status.json"

C = {"reset":"\033[0m","grn":"\033[42m\033[30m","red":"\033[41m\033[37m",
     "yel":"\033[43m\033[30m","blu":"\033[44m\033[37m","gry":"\033[100m\033[37m",
     "b":"\033[1m","dim":"\033[2m","cyan":"\033[96m"}

def verdict(run):
    g = LOGS / run / "grade.json"
    s = LOGS / run / "summary.json"
    if g.exists():
        try:
            v = json.loads(g.read_text()).get("verdict")
            if v in ("PASS","STRUCTURAL_PASS"): return "pass"
            if v in (None,"BAD_GRADE","GRADER_FAILED","MISSING_OUTPUT"): return "err"
            return "fail"
        except Exception: return "err"
    if s.exists(): return "ungraded"   # ran but not graded yet
    if (LOGS / run / "transcript.jsonl").exists(): return "running"
    return "pending"

CELL = {"pass":("grn","✓"),"fail":("red","✗"),"err":("yel","!"),
        "ungraded":("blu","·"),"running":("cyan","▶"),"pending":("gry"," ")}

def render_grid(arm, target, color=True):
    label = arm["label"]; tasks = arm.get("pertask",{})
    lines = []
    head = "  " + "".join(f"{v:>3}" for v in range(1,target+1))
    lines.append(f"{C['b'] if color else ''}{label}{C['reset'] if color else ''}   {C['dim'] if color else ''}{head}{C['reset'] if color else ''}")
    # task rows
    from_status = {t:None for t in STATUS_TASKS}
    for t in STATUS_TASKS:
        row = f"{t:<17}"
        for v in range(1,target+1):
            st = verdict(f"{t}_{label}_v{v}")
            ck, ch = CELL[st]
            if color:
                row += f" {C[ck]}{ch}{C['reset']} "
            else:
                row += f" {ch} "
        pt = tasks.get(t,{})
        row += f"  {pt.get('pass','?')}/{pt.get('done','?')}"
        lines.append(row)
    return "\n".join(lines)

def human_eta(status):
    # crude ETA: cells remaining * avg recent cell wall (from mtimes of last ~8 done summaries)
    done = status["grand_done"]; total = status["grand_total"]
    rem = total - done
    sums = sorted(LOGS.glob("p*_397b-*_v*/summary.json"), key=lambda p:p.stat().st_mtime)[-9:]
    if len(sums) >= 2:
        span = sums[-1].stat().st_mtime - sums[0].stat().st_mtime
        per = span / (len(sums)-1)
        secs = int(rem * per)
        h, m = secs//3600, (secs%3600)//60
        return f"~{h}h{m:02d}m (≈{per/60:.1f}min/cell over last {len(sums)} cells)"
    return "n/a"

STATUS_TASKS = []

def render(status, color=True):
    global STATUS_TASKS
    STATUS_TASKS = status.get("tasks", [])
    L = []
    bar_w = 40
    filled = int(bar_w * status["pct"]/100)
    bar = "█"*filled + "░"*(bar_w-filled)
    hp = "UP" if status["endpoint_up"] else "DOWN"
    hcol = C["grn"] if (status["endpoint_up"] and color) else (C["red"] if color else "")
    rs = C["reset"] if color else ""
    L.append(f"{C['b'] if color else ''}MMBT bench autopilot — N={status['target_n']} — {status['phase']}{rs}")
    L.append(f"  {bar} {status['pct']}%  ({status['grand_done']}/{status['grand_total']} cells)")
    cur = status.get("current") or {}
    L.append(f"  endpoint: {hcol}{hp}{rs}   current: {C['cyan'] if color else ''}{cur.get('cell','-')}{rs} iter={cur.get('iter','-')} frozen={cur.get('frozen_secs','-')}s")
    L.append(f"  ETA: {human_eta(status)}   updated: {status['updated']}")
    L.append("")
    for arm in status["arms"]:
        L.append(render_grid(arm, status["target_n"], color))
        L.append(f"    {arm['label']} subtotal: {sum(p['pass'] for p in arm['pertask'].values())}/{arm['done']} pass  ({arm['done']}/{arm['total']} cells)")
        L.append("")
    if color:
        L.append(f"  legend: {C['grn']}✓{rs}pass {C['red']}✗{rs}fail {C['yel']}!{rs}grader {C['blu']}·{rs}ungraded {C['cyan']}▶{rs}running {C['gry']} {rs}pending")
    return "\n".join(L)

def to_html(status):
    STATUS_TASKS_local = status.get("tasks", [])
    hc = {"pass":"#1a7f37","fail":"#b91c1c","err":"#b8860b","ungraded":"#1f5fbf","running":"#0aa","pending":"#444"}
    rows = []
    for arm in status["arms"]:
        rows.append(f"<h3>{arm['label']} — {sum(p['pass'] for p in arm['pertask'].values())}/{arm['done']} pass ({arm['done']}/{arm['total']})</h3><table style='border-collapse:collapse'>")
        hdr = "<tr><th></th>" + "".join(f"<th style='font:11px monospace;color:#888'>{v}</th>" for v in range(1,status['target_n']+1)) + "<th>p/d</th></tr>"
        rows.append(hdr)
        for t in STATUS_TASKS_local:
            cells = ""
            for v in range(1,status['target_n']+1):
                st = verdict(f"{t}_{arm['label']}_v{v}")
                cells += f"<td title='{t}_v{v}:{st}' style='width:16px;height:16px;background:{hc[st]}'></td>"
            pt = arm['pertask'].get(t,{})
            rows.append(f"<tr><td style='font:12px monospace;padding-right:6px'>{t}</td>{cells}<td style='font:11px monospace;color:#aaa'>{pt.get('pass','?')}/{pt.get('done','?')}</td></tr>")
        rows.append("</table>")
    return f"""<!doctype html><meta http-equiv=refresh content=30><body style='background:#111;color:#ddd;font-family:system-ui'>
<h2>MMBT bench autopilot — N={status['target_n']} — {status['phase']} — {status['pct']}%</h2>
<p>{status['grand_done']}/{status['grand_total']} cells · endpoint {'UP' if status['endpoint_up'] else 'DOWN'} · current {(status.get('current') or {}).get('cell','-')} iter {(status.get('current') or {}).get('iter','-')} · updated {status['updated']}</p>
{''.join(rows)}
<p style='color:#888'>green=pass red=fail yellow=grader-issue blue=ungraded teal=running grey=pending</p></body>"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--watch", action="store_true")
    ap.add_argument("--html", default=None)
    ap.add_argument("--no-color", action="store_true")
    args = ap.parse_args()
    def once():
        if not STATUS.exists():
            print("no status yet (autopilot not started?)"); return
        status = json.loads(STATUS.read_text())
        if args.html:
            Path(args.html).write_text(to_html(status)); print(f"wrote {args.html}")
        else:
            out = render(status, color=not args.no_color)
            if args.watch: os.system("clear")
            print(out)
    if args.watch:
        while True:
            once(); time.sleep(15)
    else:
        once()

if __name__ == "__main__":
    main()
