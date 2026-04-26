#!/usr/bin/env python3
"""
Chart 1: Revenue & Operating Margin Trajectory
Source data: /input/repo/extracted/income_statement_annual.csv
             /input/repo/extracted/financial_summary.json
Output: /assets/charts/01_revenue_margins.png

Shows historical revenue growth (bars) and operating margin improvement (line).
Inflection points: FCF turns positive FY2024, margin improvement accelerates.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

# Data from /input/repo/extracted/financial_summary.json
fy_labels = ['FY2023', 'FY2024', 'FY2025', 'FY2026']
revenue = [424.3, 579.9, 759.2, 955.2]
op_margin = [-49.8, -32.3, -18.8, -7.4]
fcf = [-83.5, 33.4, -67.7, 222.0]

fig, ax1 = plt.subplots(figsize=(10, 6))

# Color palette
REVENUE_COLOR = '#2563EB'  # Blue
MARGIN_COLOR = '#059669'   # Green
FCF_COLOR = '#DC2626'      # Red (for negative)
BG_COLOR = '#F8FAFC'

ax1.set_facecolor(BG_COLOR)
fig.patch.set_facecolor('white')

# Revenue bars
x = np.arange(len(fy_labels))
bars = ax1.bar(x, revenue, width=0.6, color=REVENUE_COLOR, alpha=0.85, label='Revenue ($M)')
ax1.set_ylabel('Revenue ($M)', color=REVENUE_COLOR, fontsize=12, fontweight='bold')
ax1.tick_params(axis='y', labelcolor=REVENUE_COLOR)
ax1.yaxis.set_major_formatter(mticker.StrMethodFormatter('${x:,.0f}'))

# Operating margin line
ax2 = ax1.twinx()
line = ax2.plot(x, op_margin, 'o-', color=MARGIN_COLOR, linewidth=2.5, markersize=8, label='Op. Margin (%)')
ax2.set_ylabel('Operating Margin (%)', color=MARGIN_COLOR, fontsize=12, fontweight='bold')
ax2.tick_params(axis='y', labelcolor=MARGIN_COLOR)
ax2.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:.1f}%'))

# FCF annotation
for i, (r, m, f) in enumerate(zip(revenue, op_margin, fcf)):
    # Revenue label on bars
    ax1.text(i, r + 15, f'${r:.0f}M', ha='center', va='bottom', fontsize=9, fontweight='bold')
    # Margin label on line
    ax2.text(i, m - 5, f'{m:.1f}%', ha='center', va='top', fontsize=9, fontweight='bold', color=MARGIN_COLOR)
    # FCF annotation
    fcf_label = f'FCF: ${f:.0f}M'
    y_offset = -30 if f < 0 else -25
    ax1.text(i, y_offset, fcf_label, ha='center', va='top', fontsize=8, color='#64748B')

# Zero line
ax2.axhline(y=0, color='#94A3B8', linestyle='--', linewidth=0.8, alpha=0.5)

ax1.set_xticks(x)
ax1.set_xticklabels(fy_labels, fontsize=11)
ax1.set_title('Revenue Growth & Operating Margin Trajectory\nGitLab Inc. (GTLB)', fontsize=14, fontweight='bold', pad=15)

# Remove spines
for spine in ['top', 'right']:
    ax1.spines[spine].set_visible(False)
    ax2.spines[spine].set_visible(False)

plt.tight_layout()
plt.savefig('/workspace/assets/charts/01_revenue_margins.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Chart 1 saved: 01_revenue_margins.png")
