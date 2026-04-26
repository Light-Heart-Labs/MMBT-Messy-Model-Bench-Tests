#!/usr/bin/env python3
"""
Chart 5: Risk Assessment Heat Map
Source data: /input/repo/memo/gitlab_investment_memo.md (Risk Assessment section)
Output: /assets/charts/05_risk_heatmap.png

Shows risks plotted by probability vs. impact with color coding.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Risk data from /input/repo/memo/gitlab_investment_memo.md
risks = [
    {'name': 'NRR Decline', 'prob': 0.75, 'impact': 0.9, 'color': '#DC2626', 'condition': 'NRR falls below 110%'},
    {'name': 'GitHub Competition', 'prob': 0.50, 'impact': 0.85, 'color': '#EA580C', 'condition': 'GitHub captures full DevOps workflow'},
    {'name': 'Macro Downturn', 'prob': 0.45, 'impact': 0.80, 'color': '#EA580C', 'condition': 'Recession cuts enterprise software spend'},
    {'name': 'AI Monetization Failure', 'prob': 0.40, 'impact': 0.65, 'color': '#D97706', 'condition': 'AI features fail to drive upsells'},
    {'name': 'Open-Source Cannibalization', 'prob': 0.20, 'impact': 0.70, 'color': '#D97706', 'condition': 'Self-hosted users reject paid tier'},
    {'name': 'Key Person Risk', 'prob': 0.15, 'impact': 0.50, 'color': '#64748B', 'condition': 'CEO departure without succession plan'},
]

fig, ax = plt.subplots(figsize=(11, 7))

BG_COLOR = '#F8FAFC'
ax.set_facecolor(BG_COLOR)
fig.patch.set_facecolor('white')

# Plot risk bubbles
for r in risks:
    size = max(200, (r['prob'] * r['impact']) * 2000)
    ax.scatter(r['prob'] * 100, r['impact'] * 100, s=size,
               color=r['color'], alpha=0.7, edgecolors='white', linewidth=2, zorder=3)
    ax.annotate(r['name'], (r['prob'] * 100, r['impact'] * 100),
                fontsize=9, ha='center', va='center', fontweight='bold', color='white')
    # Condition label below
    ax.annotate(r['condition'], (r['prob'] * 100, r['impact'] * 100 - 12),
                fontsize=7, ha='center', va='top', color='#475569', style='italic')

# Quadrant lines
ax.axhline(y=50, color='#94A3B8', linestyle='--', linewidth=0.8, alpha=0.5)
ax.axvline(x=50, color='#94A3B8', linestyle='--', linewidth=0.8, alpha=0.5)

# Quadrant labels
ax.text(25, 85, 'High Impact\nLow Probability', fontsize=9, ha='center', color='#64748B', alpha=0.6)
ax.text(75, 85, 'High Impact\nHigh Probability', fontsize=9, ha='center', color='#DC2626', alpha=0.6, fontweight='bold')
ax.text(25, 15, 'Low Impact\nLow Probability', fontsize=9, ha='center', color='#64748B', alpha=0.6)
ax.text(75, 15, 'Low Impact\nHigh Probability', fontsize=9, ha='center', color='#64748B', alpha=0.6)

ax.set_xlabel('Probability (%)', fontsize=12, fontweight='bold')
ax.set_ylabel('Impact on Valuation (%)', fontsize=12, fontweight='bold')
ax.set_title('Risk Assessment: Probability vs. Impact\nGitLab Inc. (GTLB)',
             fontsize=14, fontweight='bold', pad=15)

ax.set_xlim(0, 100)
ax.set_ylim(0, 100)

for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)

ax.grid(True, alpha=0.1, linestyle='--')

plt.tight_layout()
plt.savefig('/workspace/assets/charts/05_risk_heatmap.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Chart 5 saved: 05_risk_heatmap.png")
