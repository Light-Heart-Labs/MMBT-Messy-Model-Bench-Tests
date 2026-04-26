#!/usr/bin/env python3
"""
Chart 4: Bear/Base/Bull Scenario Distribution
Source data: /input/repo/memo/gitlab_investment_memo.md (Scenario Analysis table)
Output: /assets/charts/04_scenario_distribution.png

Shows probability-weighted price target distribution.
Bear (25%): $18.58, Base (50%): $38.52, Bull (25%): $88.30
Weighted: $45.98
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

# Scenario data from /input/repo/memo/gitlab_investment_memo.md
scenarios = {
    'Bear': {'price': 18.58, 'prob': 0.25, 'color': '#DC2626'},
    'Base': {'price': 38.52, 'prob': 0.50, 'color': '#2563EB'},
    'Bull': {'price': 88.30, 'prob': 0.25, 'color': '#059669'},
}
current_price = 21.51
weighted_target = 45.98

fig, ax = plt.subplots(figsize=(12, 7))

BG_COLOR = '#F8FAFC'
ax.set_facecolor(BG_COLOR)
fig.patch.set_facecolor('white')

# Create composite distribution from three normal components
x = np.linspace(0, 120, 1000)
y_total = np.zeros_like(x)

for name, s in scenarios.items():
    # Use sigma proportional to distance from mean to create realistic spread
    sigma = s['price'] * 0.25  # 25% of price as std dev
    y = s['prob'] * norm.pdf(x, s['price'], sigma)
    y_total += y
    # Fill individual component
    ax.fill_between(x, 0, y, alpha=0.3, color=s['color'], label=f'{name} ({s["prob"]*100:.0f}%) — ${s["price"]:.2f}')

# Plot total distribution
ax.plot(x, y_total, color='#1E293B', linewidth=2.5)

# Current price marker
ax.axvline(x=current_price, color='#64748B', linestyle='--', linewidth=2, label=f'Current: ${current_price:.2f}')
ax.text(current_price, ax.get_ylim()[1] * 0.95, f'Current\n${current_price:.2f}',
        fontsize=10, ha='center', va='top', fontweight='bold', color='#64748B')

# Weighted target marker
ax.axvline(x=weighted_target, color='#7C3AED', linestyle='-', linewidth=2.5, label=f'Weighted Target: ${weighted_target:.2f}')
ax.text(weighted_target, ax.get_ylim()[1] * 0.85, f'Weighted\n${weighted_target:.2f}',
        fontsize=10, ha='center', va='top', fontweight='bold', color='#7C3AED')

# Scenario price markers
for name, s in scenarios.items():
    ax.axvline(x=s['price'], color=s['color'], linestyle=':', linewidth=1.5, alpha=0.7)
    ax.text(s['price'], ax.get_ylim()[1] * 0.7, f'{name}\n${s["price"]:.2f}',
            fontsize=9, ha='center', va='top', fontweight='bold', color=s['color'])

ax.set_xlabel('Implied Price per Share ($)', fontsize=12, fontweight='bold')
ax.set_ylabel('Probability Density', fontsize=12, fontweight='bold')
ax.set_title('Probability-Weighted Price Target Distribution\nGitLab Inc. (GTLB) — 12-Month Outlook',
             fontsize=14, fontweight='bold', pad=15)

ax.set_xlim(0, 120)
ax.set_ylim(0, None)

# Remove top/right spines
for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)

ax.grid(True, alpha=0.15, axis='x')
ax.legend(loc='upper right', fontsize=9, framealpha=0.9)

plt.tight_layout()
plt.savefig('/workspace/assets/charts/04_scenario_distribution.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Chart 4 saved: 04_scenario_distribution.png")
