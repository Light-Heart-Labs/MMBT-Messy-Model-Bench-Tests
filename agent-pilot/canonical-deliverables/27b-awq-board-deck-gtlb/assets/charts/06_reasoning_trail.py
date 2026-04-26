#!/usr/bin/env python3
"""
Chart 6: Reasoning Trail — Decision Dependency Graph
Source data: /input/repo/decisions/, /input/repo/tool-log.md, commit history
Output: /assets/charts/06_reasoning_trail.png

Visualizes the agent's decision process: filings → data → analysis → decisions → conclusion.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

fig, ax = plt.subplots(figsize=(14, 10))

BG_COLOR = '#F8FAFC'
ax.set_facecolor(BG_COLOR)
fig.patch.set_facecolor('white')

# Define nodes as (x, y, label, color, width, height)
nodes = [
    # Row 1: Data Sources (y=8)
    (1.5, 8.0, 'SEC Filings\n(10-K, 10-Q)\n[Blocked 403]', '#94A3B8', 1.8, 0.8),
    (4.5, 8.0, 'yfinance API\n[Primary Source]', '#2563EB', 1.8, 0.8),
    (7.5, 8.0, 'Earnings Call\nTranscripts\n[6 files]', '#7C3AED', 1.8, 0.8),
    (10.5, 8.0, 'Competitor\nData\n[yfinance]', '#059669', 1.8, 0.8),

    # Row 2: Data Extraction (y=6)
    (4.5, 6.0, 'Financial Data\n[Income, BS, CF]', '#2563EB', 1.8, 0.6),
    (7.5, 6.0, 'ARR/NRR\n[Transcripts]', '#7C3AED', 1.5, 0.6),
    (10.5, 6.0, 'Comp Set\n[8 companies]', '#059669', 1.5, 0.6),

    # Row 3: Analysis (y=4)
    (2.5, 4.0, 'Company\nSelection\n[ADR-001]', '#D97706', 1.5, 0.6),
    (5.5, 4.0, 'Three-Statement\nModel\n[Projections]', '#2563EB', 1.8, 0.6),
    (8.5, 4.0, 'Competitor\nSelection\n[ADR-002]', '#D97706', 1.5, 0.6),
    (11.0, 4.0, 'Valuation\nMethodology\n[ADR-003]', '#D97706', 1.5, 0.6),

    # Row 4: Decisions (y=2)
    (3.5, 2.0, 'DCF Base Case\n[$38.52/share]', '#2563EB', 1.8, 0.6),
    (6.5, 2.0, 'EV/Revenue\nPeer Avg\n[$53.25/share]', '#059669', 1.8, 0.6),
    (9.5, 2.0, 'Scenario\nAnalysis\n[3 scenarios]', '#7C3AED', 1.8, 0.6),

    # Row 5: Conclusion (y=0.5)
    (6.5, 0.5, 'BUY Recommendation\n$42.00 Target\n95% Upside', '#059669', 3.0, 0.8),
]

# Draw nodes
for x, y, label, color, w, h in nodes:
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                          boxstyle="round,pad=0.08",
                          facecolor=color, edgecolor='white',
                          linewidth=2, alpha=0.85, zorder=3)
    ax.add_patch(box)
    ax.text(x, y, label, fontsize=8, ha='center', va='center',
            fontweight='bold', color='white', zorder=4)

# Draw arrows
arrows = [
    # Data sources → extraction
    (4.5, 8.0, 4.5, 6.0),  # yfinance → financial data
    (7.5, 8.0, 7.5, 6.0),  # transcripts → ARR/NRR
    (10.5, 8.0, 10.5, 6.0),  # competitor data → comp set

    # Extraction → analysis
    (4.5, 6.0, 2.5, 4.0),  # financial data → company selection
    (4.5, 6.0, 5.5, 4.0),  # financial data → model
    (7.5, 6.0, 5.5, 4.0),  # ARR/NRR → model
    (10.5, 6.0, 8.5, 4.0),  # comp set → competitor selection
    (10.5, 6.0, 11.0, 4.0),  # comp set → valuation methodology

    # Analysis → decisions
    (5.5, 4.0, 3.5, 2.0),  # model → DCF
    (8.5, 4.0, 6.5, 2.0),  # competitor selection → EV/Revenue
    (11.0, 4.0, 9.5, 2.0),  # valuation methodology → scenario analysis
    (5.5, 4.0, 9.5, 2.0),  # model → scenario analysis

    # Decisions → conclusion
    (3.5, 2.0, 6.5, 0.5),  # DCF → conclusion
    (6.5, 2.0, 6.5, 0.5),  # EV/Revenue → conclusion
    (9.5, 2.0, 6.5, 0.5),  # scenario analysis → conclusion
]

for x1, y1, x2, y2 in arrows:
    arrow = FancyArrowPatch((x1, y1 - 0.35), (x2, y2 + 0.35),
                           arrowstyle='->', mutation_scale=15,
                           color='#475569', linewidth=1.5, alpha=0.5,
                           connectionstyle="arc3,rad=0.1", zorder=2)
    ax.add_patch(arrow)

# Section labels
ax.text(0.3, 8.0, 'DATA\nSOURCES', fontsize=9, fontweight='bold', color='#64748B', va='center')
ax.text(0.3, 6.0, 'EXTRACTION', fontsize=9, fontweight='bold', color='#64748B', va='center')
ax.text(0.3, 4.0, 'ANALYSIS', fontsize=9, fontweight='bold', color='#64748B', va='center')
ax.text(0.3, 2.0, 'DECISIONS', fontsize=9, fontweight='bold', color='#64748B', va='center')
ax.text(0.3, 0.5, 'CONCLUSION', fontsize=9, fontweight='bold', color='#059669', va='center')

ax.set_xlim(0, 13)
ax.set_ylim(0, 9.5)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('Reasoning Trail: How the Agent Moved from Data to Recommendation\nGitLab Inc. (GTLB)',
             fontsize=14, fontweight='bold', pad=15)

plt.tight_layout()
plt.savefig('/workspace/assets/charts/06_reasoning_trail.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Chart 6 saved: 06_reasoning_trail.png")
