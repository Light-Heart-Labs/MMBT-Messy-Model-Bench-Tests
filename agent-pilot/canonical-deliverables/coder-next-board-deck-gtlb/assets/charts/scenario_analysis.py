#!/usr/bin/env python3
"""
Scenario Analysis Chart
Generates: Probability-weighted scenario visualization (bear/base/bull)
"""

import matplotlib.pyplot as plt
import os

# Set style
plt.style.use('default')
plt.rcParams['figure.facecolor'] = '#FAFAFA'
plt.rcParams['axes.facecolor'] = '#FAFAFA'
plt.rcParams['axes.edgecolor'] = '#E0E0E0'
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.color'] = '#E0E0E0'
plt.rcParams['font.family'] = 'Arial'

# Colors
COLOR_BEAR = '#D32F2F'    # Red
COLOR_BASE = '#388E3C'    # Green
COLOR_BULL = '#1976D2'    # Blue
COLOR_WEIGHTED = '#1E88E5'  # GitLab blue

# Scenario data (from memo)
scenarios = [
    {'name': 'Bear', 'price': 18.58, 'probability': 0.25, 'color': COLOR_BEAR},
    {'name': 'Base', 'price': 38.52, 'probability': 0.50, 'color': COLOR_BASE},
    {'name': 'Bull', 'price': 88.30, 'probability': 0.25, 'color': COLOR_BULL},
]

# Calculate probability-weighted target
weighted_target = sum(s['price'] * s['probability'] for s in scenarios)

# Create figure
fig, ax = plt.subplots(figsize=(10, 6))
fig.suptitle('Scenario Analysis: Probability-Weighted Target', fontsize=16, fontweight='bold')

# Create horizontal bar chart for scenarios
y_pos = range(len(scenarios))
prices = [s['price'] for s in scenarios]
probabilities = [s['probability'] * 100 for s in scenarios]  # Convert to %
colors = [s['color'] for s in scenarios]

bars = ax.barh(y_pos, prices, color=colors, alpha=0.7, edgecolor='black', linewidth=1)

# Add probability labels
for i, (bar, prob) in enumerate(zip(bars, probabilities)):
    ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2, 
            f'{prob}%', va='center', fontsize=11, fontweight='bold')

# Add price labels
for i, (bar, price) in enumerate(zip(bars, prices)):
    ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2, 
            f'${price:.2f}', va='center', fontsize=10)

# Add probability-weighted target line
ax.axvline(x=weighted_target, color=COLOR_WEIGHTED, linestyle='-', linewidth=3, 
           label=f'Probability-Weighted Target (${weighted_target:.2f})')

# Add weighted target label
ax.text(weighted_target + 2, -0.2, f'${weighted_target:.2f}', 
        va='center', fontsize=12, fontweight='bold', color=COLOR_WEIGHTED)

# Set labels
ax.set_xlabel('Implied Price ($)', fontsize=12)
ax.set_yticks(y_pos)
ax.set_yticklabels([f"{s['name']} ({s['probability']*100:.0f}%)" for s in scenarios])
ax.set_xlim(0, 100)
ax.legend(loc='lower right', fontsize=10)

# Add current price reference (from company_info.json)
current_price = 21.51
ax.axvline(x=current_price, color='gray', linestyle='--', linewidth=1, alpha=0.5)
ax.text(current_price + 1, 3.2, f'Current Price: ${current_price:.2f}', 
        va='center', fontsize=9, color='gray')

plt.tight_layout()
plt.savefig('/workspace/assets/charts/scenario_analysis.png', dpi=150, 
            bbox_inches='tight', facecolor='#FAFAFA')
plt.close()

print("Scenario analysis chart generated: /workspace/assets/charts/scenario_analysis.png")
