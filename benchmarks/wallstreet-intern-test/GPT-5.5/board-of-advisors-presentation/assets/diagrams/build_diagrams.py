from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets/diagrams"

INK = "#17212B"
MUTED = "#607080"
PAPER = "#F7F4EC"
BLUE = "#2A6FDB"
GREEN = "#27AE60"
RED = "#D64A4A"
AMBER = "#D99A2B"
PURPLE = "#7A4CC2"
TEAL = "#009CA6"
GRID = "#D9E1E8"


def font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


F_TITLE = font(42, True)
F_SUB = font(24)
F_BODY = font(21)
F_SMALL = font(17)
F_LABEL = font(18, True)


def canvas(title, subtitle=""):
    im = Image.new("RGB", (1600, 900), PAPER)
    d = ImageDraw.Draw(im)
    d.text((70, 42), title, fill=INK, font=F_TITLE)
    if subtitle:
        d.text((72, 94), subtitle, fill=MUTED, font=F_SUB)
    return im, d


def box(d, xy, title, subtitle, color):
    d.rounded_rectangle(xy, radius=18, fill="white", outline=color, width=4)
    x0, y0, x1, y1 = xy
    d.rectangle((x0, y0, x0 + 12, y1), fill=color)
    d.text((x0 + 28, y0 + 22), title, fill=INK, font=F_LABEL)
    d.text((x0 + 28, y0 + 54), subtitle, fill=MUTED, font=F_SMALL)


def arrow(d, start, end, color=INK):
    d.line((start, end), fill=color, width=4)
    ex, ey = end
    sx, sy = start
    if ex >= sx:
        pts = [(ex, ey), (ex - 16, ey - 8), (ex - 16, ey + 8)]
    else:
        pts = [(ex, ey), (ex + 16, ey - 8), (ex + 16, ey + 8)]
    d.polygon(pts, fill=color)


def reasoning_graph():
    im, d = canvas("Reasoning Trail Graph", "How the agent moved from source files to a restrained recommendation.")
    nodes = {
        "raw": (90, 190, 390, 300, "Raw evidence", "SEC, transcripts, PRs", BLUE),
        "extract": (500, 190, 800, 300, "Extraction", "CSV + line indices", TEAL),
        "model": (910, 190, 1210, 300, "Model", "3-statement + checks", GREEN),
        "memo": (1320, 190, 1540, 300, "Memo", "HOLD / $41", AMBER),
        "adr": (500, 430, 800, 540, "ADRs", "Peers, WACC, valuation", PURPLE),
        "dead": (910, 430, 1210, 540, "Rejected theses", "No forced sell-side miss", RED),
        "audit": (700, 650, 1040, 760, "Audit trail", "Trace IDs, hashes, reconciliation", INK),
    }
    for n in nodes.values():
        box(d, n[:4], n[4], n[5], n[6])
    arrow(d, (390, 245), (500, 245), BLUE)
    arrow(d, (800, 245), (910, 245), TEAL)
    arrow(d, (1210, 245), (1320, 245), GREEN)
    arrow(d, (650, 300), (650, 430), PURPLE)
    arrow(d, (1060, 300), (1060, 430), RED)
    arrow(d, (650, 540), (790, 650), PURPLE)
    arrow(d, (1060, 540), (950, 650), RED)
    arrow(d, (1430, 300), (1020, 650), AMBER)
    d.text((90, 810), "Key capability signal: the agent documented uncertainty and rejected an attractive-but-unsupported BUY thesis.", fill=INK, font=F_BODY)
    im.save(OUT / "reasoning_graph.png")


def audit_workflow():
    im, d = canvas("How To Audit This Deck", "A board member should be able to verify any claim in minutes.")
    steps = [
        ("Pick a slide claim", "Every slide points to audit/traces/slide-XX.md"),
        ("Open trace file", "Find trace ID, source chain, and input commit"),
        ("Inspect input repo", "Use /input/repo path + line or model cell"),
        ("Land on raw evidence", "10-K, transcript, source page, or model output"),
    ]
    x = 110
    colors = [BLUE, TEAL, AMBER, GREEN]
    for idx, (title, sub) in enumerate(steps, start=1):
        x0 = x + (idx - 1) * 360
        d.ellipse((x0, 250, x0 + 84, 334), fill=colors[idx - 1])
        d.text((x0 + 30, 272), str(idx), fill="white", font=font(30, True))
        d.text((x0 - 10, 380), title, fill=INK, font=F_LABEL)
        d.text((x0 - 10, 414), sub, fill=MUTED, font=F_SMALL)
        if idx < 4:
            arrow(d, (x0 + 100, 292), (x0 + 300, 292), colors[idx - 1])
    d.text((120, 650), "The audit files are part of the deck repo, while the evidence remains anchored to input commit 8bb17db.", fill=INK, font=F_BODY)
    im.save(OUT / "audit_workflow.png")


def decision_tree():
    im, d = canvas("What Would Change The Call?", "The agent made HOLD falsifiable.")
    root = (650, 180, 950, 270, "Current call", "HOLD / $41", BLUE)
    box(d, root[:4], root[4], root[5], root[6])
    branches = [
        (120, 460, 420, 570, "Upgrade path", "Tariff relief + US recovery + intl beat", GREEN),
        (650, 460, 950, 570, "Stay HOLD", "Balanced upside/risk", AMBER),
        (1180, 460, 1480, 570, "Downgrade path", "Tariffs persist + category weakens", RED),
    ]
    for b in branches:
        box(d, b[:4], b[4], b[5], b[6])
        arrow(d, ((root[0] + root[2]) // 2, root[3]), ((b[0] + b[2]) // 2, b[1]), b[6])
    d.text((120, 700), "This slide is deliberately conditional: it makes the recommendation testable rather than final-sounding.", fill=INK, font=F_BODY)
    im.save(OUT / "decision_tree.png")


def build_all():
    OUT.mkdir(parents=True, exist_ok=True)
    reasoning_graph()
    audit_workflow()
    decision_tree()
    print("Built diagrams in assets/diagrams")


if __name__ == "__main__":
    build_all()
