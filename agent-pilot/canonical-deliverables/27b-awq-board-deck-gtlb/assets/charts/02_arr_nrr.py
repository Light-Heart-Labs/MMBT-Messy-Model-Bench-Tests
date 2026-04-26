#!/usr/bin/env python3
"""
Chart 2: ARR Growth with NRR Overlay
Source data: /input/repo/extracted/financial_summary.json
Output: /assets/charts/02_arr_nrr.png

Shows ARR growth trajectory and NRR trend.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# Data from /input/repo/extracted/financial_summary.json
fy_labels = ['FY2022', 'FY2023', 'FY2024', 'FY2025', 'FY2026']
arr = [300, 400, 530, 680, 860]
nrr = [120, 118, 117, 116, 115]

fig, ax1 = plt.subplots(figsize=(10, 6))

BG_COLOR = '#F8FAFC'
ARR_COLOR = '#7C3AED'  # Purple
NRR_COLOR = '#EA580C'  # Orange

ax1.set_facecolor(BG_COLOR)
fig.patch.set_facecolor('white')

x = np.arange(len(fy_labels))

# ARR bars
bars = ax1.bar(x, arr, width=0.6, color=ARR_COLOR, alpha=0.85, label='ARR ($M)')
ax1.set_ylabel('ARR ($M)', color=ARR_COLOR, fontsize=12, fontweight='bold')
ax1.tick_params(axis='y', labelcolor=ARR_COLOR)
ax1.yaxis.set_major_formatter(mticker.StrMethodFormatter('${x:,.0f}M'))

# NRR line
ax2 = ax1.twinx()
line = ax2.plot(x, nrr, 's-', color=NRR_COLOR, linewidth=2.5, markersize=8, label='NRR (%)')
ax2.set_ylabel('Net Revenue Retention (%)', color=NRR_COLOR, fontsize=12, fontweight='bold')
ax2.tick_params(axis='y', labelcolor=NRR_COLOR)
ax2.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:.0f}%'))
ax2.set_ylim(105, 125)

# Annotations
for i, (a, n) in enumerate(zip(arr, nrr)):
    ax1.text(i, a + 15, f'${a}M', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax2.text(i, n + 1.5, f'{n}%', ha='center', va='bottom', fontsize=9, fontweight='bold', color=NRR_COLOR)

# 115% threshold line
ax2.axhline(y=115, color='#94A3B8', linestyle='--', linewidth=0.8, alpha=0.5)
ax2.text(len(fy_labels)-0.3, 115.5, '115% threshold', fontsize=8, color='#64748B')

ax1.set_xticks(x)
ax1.set_xticklabels(fy_labels, fontsize=11)
ax1.set_title('ARR Growth & Net Revenue Retention\nGitLab Inc. (GTLB)', fontsize=14, fontweight='bold', pad=15)

for spine in ['top', 'right']:
    ax1.spines[spine].set_visible(False)
    ax2.spines[spine].set_visible(False)

plt.tight_layout()
plt.savefig('/workspace/assets/charts/02_arr_nrr.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Chart 2 saved: 02_arr_nrr.png")
