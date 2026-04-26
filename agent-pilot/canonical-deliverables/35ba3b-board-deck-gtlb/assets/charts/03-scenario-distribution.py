#!/usr/bin/env python3
"""
Chart 3: Bear/Base/Bull Scenario Distribution
Probability-weighted visualization of price targets.

Source data: /input/repo/memo/gitlab_investment_memo.md (Scenario Analysis section)
Reproduces: Slide 8 of the deck
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

# Colors
TEAL = '#0D9488'
RED = '#DC2626'
BLUE = '#2563EB'
GREEN = '#16A34A'
GRAY = '#6B7280'

# Scenario data from memo
scenarios = {
    'Bear': {'price': 18.58, 'prob': 0.25, 'color': RED},
    'Base': {'price': 38.52, 'prob': 0.50, 'color': BLUE},
    'Bull': {'price': 88.30, 'prob': 0.25, 'color': GREEN}
}

expected_value = 45.98  # Probability-weighted target
target_12m = 42.00      # 12-month price target
current_price = 21.51

# Create figure with two subplots: histogram + bar chart
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), gridspec_kw={'width_ratios': [3, 2]})

# --- LEFT: Probability Distribution (Histogram) ---
np.random.seed(42)
bear_samples = np.random.normal(18.58, 5, 2500)
base_samples = np.random.normal(38.52, 10, 5000)
bull_samples = np.random.normal(88.30, 20, 2500)

all_samples = np.concatenate([bear_samples, base_samples, bull_samples])
all_samples = all_samples[(all_samples > 0) & (all_samples < 120)]

# Histogram
ax1.hist(all_samples, bins=50, color=TEAL, alpha=0.3, edgecolor='white', linewidth=0.5)

# Mark scenario points
for name, s in scenarios.items():
    ax1.axvline(x=s['price'], color=s['color'], linestyle='--', alpha=0.7, linewidth=2)
    ax1.fill_betweenx([0, ax1.get_ylim()[1]], s['price']-3, s['price']+3, 
                       color=s['color'], alpha=0.3)
    ax1.annotate(f"{name}\n${s['price']:.0f}", 
                 xy=(s['price'], ax1.get_ylim()[1]*0.85),
                 xytext=(0, 15), textcoords='offset points',
                 fontsize=11, fontweight='bold', color=s['color'], ha='center')
    ax1.annotate(f"{int(s['prob']*100)}%", 
                 xy=(s['price'], ax1.get_ylim()[1]*0.7),
                 fontsize=9, color=s['color'], ha='center', alpha=0.8)

# Mark expected value
ax1.axvline(x=expected_value, color='black', linestyle='-', linewidth=2.5, alpha=0.8)
ax1.annotate(f'Expected Value\n${expected_value:.0f}', 
             xy=(expected_value, ax1.get_ylim()[1]*0.95),
             xytext=(0, 15), textcoords='offset points',
             fontsize=12, fontweight='bold', color='black', ha='center')

# Mark 12-month target
ax1.axvline(x=target_12m, color='purple', linestyle='-.', linewidth=2, alpha=0.7)
ax1.annotate(f'12-Month Target\n${target_12m:.0f}', 
             xy=(target_12m, ax1.get_ylim()[1]*0.65),
             xytext=(0, -20), textcoords='offset points',
             fontsize=10, fontweight='bold', color='purple', ha='center')

# Mark current price
ax1.axvline(x=current_price, color='gray', linestyle=':', linewidth=2, alpha=0.5)
ax1.annotate(f'Current\n${current_price:.0f}', 
             xy=(current_price, ax1.get_ylim()[1]*0.5),
             xytext=(0, -20), textcoords='offset points',
             fontsize=9, color='gray', ha='center')

ax1.set_xlabel('Implied Share Price ($)', fontsize=13, fontweight='bold')
ax1.set_ylabel('Frequency', fontsize=12)
ax1.set_title('Price Target Distribution: Bear / Base / Bull Scenarios\n' +
              'Probability-weighted expected value: $45.98 | 12-month target: $42.00',
              fontsize=14, fontweight='bold', pad=15)
ax1.grid(True, alpha=0.2)

# --- RIGHT: Upside/Downside Summary ---
upside_bull = (88.30 - 21.51) / 21.51 * 100
upside_base = (38.52 - 21.51) / 21.51 * 100
downside_bear = (18.58 - 21.51) / 21.51 * 100
upside_expected = (45.98 - 21.51) / 21.51 * 100

categories = ['Bear\n(25%)', 'Base\n(50%)', 'Bull\n(25%)', 'Expected\nValue']
upside_vals = [downside_bear, upside_base, upside_bull, upside_expected]
bar_colors = [RED, BLUE, GREEN, 'black']

bars = ax2.barh(categories, upside_vals, color=bar_colors, alpha=0.7, edgecolor='white', linewidth=1.5)

# Add value labels
for i, (bar, val) in enumerate(zip(bars, upside_vals)):
    label = f'{val:+.0f}%'
    if val < 0:
        ax2.text(val - 3, bar.get_y() + bar.get_height()/2, label, 
                va='center', ha='right', fontsize=11, fontweight='bold', color=RED)
    else:
        ax2.text(val + 3, bar.get_y() + bar.get_height()/2, label, 
                va='center', ha='left', fontsize=11, fontweight='bold', color=bar_colors[i])

ax2.axvline(x=0, color='black', linestyle='-', linewidth=1)
ax2.set_xlabel('Upside / Downside from Current ($21.51)', fontsize=12, fontweight='bold')
ax2.set_title('Scenario Returns', fontsize=13, fontweight='bold', pad=15)
ax2.grid(True, alpha=0.2, axis='x')

plt.tight_layout()
os.makedirs('/workspace/assets/charts', exist_ok=True)
plt.savefig('/workspace/assets/charts/03-scenario-distribution.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.savefig('/workspace/assets/charts/03-scenario-distribution.svg', bbox_inches='tight', facecolor='white')
print("Chart 3 saved: 03-scenario-distribution.png")
