#!/usr/bin/env python3
"""
Chart 4: SaaS Metrics — ARR Growth and NRR Trend
Shows the quality of GitLab's recurring revenue.

Source data: /input/repo/extracted/financial_summary.json
Reproduces: Part of Slide 4 (Financial Trajectory)
"""

import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

TEAL = '#0D9488'
BLUE = '#2563EB'
RED = '#DC2626'

with open('/input/repo/extracted/financial_summary.json', 'r') as f:
    data = json.load(f)

fy_labels = data['fy_labels'][1:]  # FY2023-FY2026
arr = data['arr'][1:]  # [400, 530, 680, 860]
nrr = data['nrr'][1:]  # [118, 117, 116, 115]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# ARR Growth
bars = ax1.bar(fy_labels, arr, color=TEAL, alpha=0.7, edgecolor='white', linewidth=1.5)
ax1.set_ylabel('ARR ($M)', fontsize=12, fontweight='bold')
ax1.set_xlabel('Fiscal Year', fontsize=12, fontweight='bold')
ax1.set_title('ARR Growth: $400M → $860M (FY2023-FY2026)', fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.2, axis='y')

# Add value labels on bars
for bar, val in zip(bars, arr):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 15,
             f'${val}M', ha='center', fontsize=11, fontweight='bold', color=TEAL)

# NRR Trend
ax2.plot(fy_labels, nrr, color=RED, linewidth=3, marker='o', markersize=10)
ax2.fill_between(range(len(fy_labels)), nrr, alpha=0.1, color=RED)
ax2.set_ylabel('Net Revenue Retention (%)', fontsize=12, fontweight='bold')
ax2.set_xlabel('Fiscal Year', fontsize=12, fontweight='bold')
ax2.set_title('NRR Trend: 118% → 115% (Declining but Still Strong)', fontsize=13, fontweight='bold')
ax2.set_ylim(110, 122)
ax2.grid(True, alpha=0.2)

# Add value labels
for i, (label, val) in enumerate(zip(fy_labels, nrr)):
    ax2.annotate(f'{val}%', (i, val), xytext=(0, 12), textcoords='offset points',
                 ha='center', fontsize=11, fontweight='bold', color=RED)

# Add 110% threshold line
ax2.axhline(y=110, color='gray', linestyle='--', alpha=0.5, linewidth=1)
ax2.text(len(fy_labels)-0.5, 110.5, '110% threshold', fontsize=8, color='gray', ha='right')

plt.tight_layout()
os.makedirs('/workspace/assets/charts', exist_ok=True)
plt.savefig('/workspace/assets/charts/04-saas-metrics.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.savefig('/workspace/assets/charts/04-saas-metrics.svg', bbox_inches='tight', facecolor='white')
print("Chart 4 saved: 04-saas-metrics.png")
