#!/usr/bin/env python3
"""
Chart 1: Financial Trajectory — Revenue, Operating Margin, FCF
Shows historical and projected financial trajectory with inflection points.

Source data: /input/repo/extracted/income_statement_annual.csv, cash_flow_annual.csv, financial_summary.json
Reproduces: Slide 4 of the deck
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import json
import os

# Colors
TEAL = '#0D9488'
BLUE = '#2563EB'
RED = '#DC2626'
GREEN = '#16A34A'

# Load data
with open('/input/repo/extracted/financial_summary.json', 'r') as f:
    data = json.load(f)

fy_labels = data['fy_labels']  # ['FY2022', 'FY2023', 'FY2024', 'FY2025', 'FY2026']
revenue = data['revenue']       # [NaN, 424.336, 579.906, 759.249, 955.224]
op_income = data['op_income']
fcf = data['fcf']

# Historical data (drop NaN)
hist_fy = fy_labels[1:]  # FY2023-FY2026
hist_rev = [r for r in revenue[1:] if not pd.isna(r)]
hist_opm = [op/r*100 for op, r in zip(op_income[1:], revenue[1:]) if not pd.isna(op) and not pd.isna(r)]
hist_fcf = [f for f in fcf[1:] if not pd.isna(f)]

# Projected data (from memo)
proj_fy = ['FY2027E', 'FY2028E', 'FY2029E', 'FY2030E', 'FY2031E']
proj_rev = [1146, 1352, 1555, 1742, 1916]
proj_opm = [-5.2, -2.0, 1.5, 3.5, 5.5]
proj_fcf = [230, 298, 373, 436, 498]

# Combined
all_fy = hist_fy + proj_fy
all_rev = hist_rev + proj_rev
all_opm = hist_opm + proj_opm
all_fcf = hist_fcf + proj_fcf

n_hist = len(hist_fy)

# Create figure
fig, ax1 = plt.subplots(figsize=(14, 8))

# Revenue (left axis)
x_hist = list(range(n_hist))
x_proj = list(range(n_hist, n_hist + len(proj_fy)))

ax1.plot(x_hist, hist_rev, color=TEAL, linewidth=3, marker='o', markersize=8, label='Revenue (Historical)')
ax1.plot(x_proj, proj_rev, color=TEAL, linewidth=3, marker='o', markersize=8, 
         label='Revenue (Projected)', linestyle='--', alpha=0.7)
ax1.fill_between(x_hist, hist_rev, alpha=0.1, color=TEAL)
ax1.fill_between(x_proj, proj_rev, alpha=0.05, color=TEAL)

# Operating Margin (right axis)
ax2 = ax1.twinx()
ax2.plot(x_hist, hist_opm, color=BLUE, linewidth=2.5, marker='s', markersize=7, 
         label='Operating Margin (Historical)')
ax2.plot(x_proj, proj_opm, color=BLUE, linewidth=2.5, marker='s', markersize=7,
         label='Operating Margin (Projected)', linestyle='--', alpha=0.7)

# FCF (secondary right axis)
ax3 = ax1.twinx()
ax3.spines['right'].position = ('outward', 60)
ax3.plot(x_hist, hist_fcf, color=RED, linewidth=2, marker='^', markersize=7,
         label='FCF (Historical)')
ax3.plot(x_proj, proj_fcf, color=GREEN, linewidth=2, marker='^', markersize=7,
         label='FCF (Projected)', linestyle='--', alpha=0.7)

# Mark inflection points
ax1.annotate('FCF turns positive\nFY2024 ($33M)', xy=(2, hist_rev[2]), xytext=(2.5, hist_rev[2]+100),
            arrowprops=dict(arrowstyle='->', color=RED, lw=2),
            fontsize=10, color=RED, fontweight='bold')

ax1.annotate('Operating margin\nimproving rapidly', xy=(3, hist_rev[3]), xytext=(3.5, hist_rev[3]+150),
            arrowprops=dict(arrowstyle='->', color=BLUE, lw=2),
            fontsize=10, color=BLUE, fontweight='bold')

# Labels
ax1.set_xlabel('Fiscal Year', fontsize=14, fontweight='bold')
ax1.set_ylabel('Revenue ($M)', fontsize=12, color=TEAL)
ax2.set_ylabel('Operating Margin (%)', fontsize=12, color=BLUE)
ax3.set_ylabel('Free Cash Flow ($M)', fontsize=12, color=RED)

ax1.set_xticks(list(range(len(all_fy))))
ax1.set_xticklabels(all_fy, rotation=45, ha='right')

ax1.tick_params(axis='y', labelcolor=TEAL)
ax2.tick_params(axis='y', labelcolor=BLUE)
ax3.tick_params(axis='y', labelcolor=RED)

# Grid
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.set_axisbelow(True)

# Legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
lines3, labels3 = ax3.get_legend_handles_labels()
ax1.legend(lines1 + lines2 + lines3, labels1 + labels2 + labels3, 
           loc='upper left', fontsize=9, framealpha=0.9)

# Title
ax1.set_title('GitLab (GTLB) Financial Trajectory: Revenue, Margin & FCF\n' + 
              'Source: /input/repo/extracted/income_statement_annual.csv, cash_flow_annual.csv, financial_summary.json',
              fontsize=16, fontweight='bold', pad=20)

plt.tight_layout()
os.makedirs('/workspace/assets/charts', exist_ok=True)
plt.savefig('/workspace/assets/charts/01-financial-trajectory.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.savefig('/workspace/assets/charts/01-financial-trajectory.svg', bbox_inches='tight', facecolor='white')
print("Chart 1 saved: 01-financial-trajectory.png")
