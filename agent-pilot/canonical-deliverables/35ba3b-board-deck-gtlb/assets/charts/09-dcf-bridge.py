#!/usr/bin/env python3
"""
Chart 9: DCF Bridge — How We Get from $21.51 to $42
Shows the step-by-step valuation bridge.

Source data: /input/repo/memo/gitlab_investment_memo.md (Valuation section)
Reproduces: Slide 9 of the deck
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

TEAL = '#0D9488'
BLUE = '#2563EB'
RED = '#DC2626'
GREEN = '#16A34A'
GRAY = '#6B7280'

# DCF bridge data
steps = [
    ('Current Price', 21.51, GRAY),
    ('Revenue Growth\n(20% CAGR)', 12.00, TEAL),
    ('Margin Expansion\n(-7% → +5%)', 8.50, BLUE),
    ('FCF Conversion\n(25% margin)', 5.00, BLUE),
    ('Terminal Value\n(3% growth)', 3.00, BLUE),
    ('Peer Multiple\n(7.0x EV/Rev)', 4.50, GREEN),
    ('Risk Discount\n(uncertainty)', -2.51, RED),
    ('Target Price', 42.00, TEAL),
]

fig, ax = plt.subplots(figsize=(14, 8))

x_pos = list(range(len(steps)))
values = [s[1] for s in steps]
colors = [s[2] for s in steps]
labels = [s[0] for s in steps]

# Waterfall-style bar chart
cumulative = 0
bar_width = 0.6

for i, (label, value, color) in enumerate(steps):
    if i == 0:
        # Starting point
        bottom = 0
        height = value
    elif i == len(steps) - 1:
        # Final target
        bottom = cumulative
        height = value
    else:
        # Intermediate steps
        bottom = cumulative
        height = value
    
    ax.bar(i, height, width=bar_width, bottom=bottom, 
           color=color, alpha=0.7, edgecolor='white', linewidth=1.5, zorder=3)
    
    # Add value label
    if i == 0:
        ax.text(i, height/2, f'${value:.0f}', ha='center', va='center',
                fontsize=12, fontweight='bold', color='white', zorder=4)
    elif i == len(steps) - 1:
        ax.text(i, bottom + height/2, f'${value:.0f}', ha='center', va='center',
                fontsize=12, fontweight='bold', color='white', zorder=4)
    else:
        ax.text(i, bottom + height + 0.5, f'+${value:.0f}', ha='center', va='bottom',
                fontsize=10, fontweight='bold', color=color, zorder=4)
    
    cumulative += value

# Add connecting lines
for i in range(len(steps) - 1):
    if i == 0:
        y_start = values[0]
    else:
        y_start = sum(values[:i+1])
    y_end = sum(values[:i+2])
    ax.plot([i + bar_width/2, i + 1 - bar_width/2], [y_start, y_end],
            'k--', alpha=0.3, linewidth=1, zorder=1)

# Labels
ax.set_xticks(x_pos)
ax.set_xticklabels(labels, fontsize=10, fontweight='bold', rotation=30, ha='right')
ax.set_ylabel('Price ($)', fontsize=12, fontweight='bold')
ax.set_title('DCF Bridge: From $21.51 Current Price to $42.00 Target\n' +
             'Source: /input/repo/memo/gitlab_investment_memo.md (Valuation section)\n' +
             'Each bar shows the contribution of a valuation component',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.2, axis='y')
ax.set_ylim(0, 50)

plt.tight_layout()
os.makedirs('/workspace/assets/charts', exist_ok=True)
plt.savefig('/workspace/assets/charts/09-dcf-bridge.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.savefig('/workspace/assets/charts/09-dcf-bridge.svg', bbox_inches='tight', facecolor='white')
print("Chart 9 saved: 09-dcf-bridge.png")
