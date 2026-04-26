#!/usr/bin/env python3
"""
Chart 2: Competitive Position — Growth vs. Margin Scatter Plot
Shows GitLab's position relative to 8 comparable companies.

Source data: /input/repo/extracted/competitor_data.json
Reproduces: Slide 5 of the deck
"""

import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

# Colors
TEAL = '#0D9488'
BLUE = '#2563EB'
RED = '#DC2626'
GREEN = '#16A34A'
GRAY = '#6B7280'
ORANGE = '#F59E0B'
PURPLE = '#8B5CF6'
PINK = '#EC4899'
INDIGO = '#4F46E5'
CYAN = '#06B6D4'

# Load competitor data
with open('/input/repo/extracted/competitor_data.json', 'r') as f:
    comp_data = json.load(f)

# Select 8 most relevant comps (exclude Doximity - healthcare, Palo Alto - too large)
relevant_comps = ['TEAM', 'DDOG', 'MDB', 'CFLT', 'SNOW', 'ZS', 'OKTA', 'BILL']
comp_colors = {
    'TEAM': BLUE, 'DDOG': GREEN, 'MDB': ORANGE, 'CFLT': PURPLE,
    'SNOW': PINK, 'ZS': INDIGO, 'OKTA': CYAN, 'BILL': GRAY
}

# GitLab data
gtlb = comp_data['GTLB']
gtlb_rev_growth = gtlb['revenue_growth'] * 100  # 23.2%
gtlb_op_margin = gtlb['operating_margin'] * 100  # -1.0%
gtlb_ev_rev = gtlb['ev_revenue']  # 2.559

# Build scatter data
names = []
x_vals = []  # revenue growth
y_vals = []  # operating margin
sizes = []   # market cap (scaled)
colors = []

for ticker in relevant_comps:
    c = comp_data[ticker]
    names.append(c['name'])
    x_vals.append(c['revenue_growth'] * 100)
    y_vals.append(c['operating_margin'] * 100)
    sizes.append(c['market_cap_b'] * 2)  # scale for visibility
    colors.append(comp_colors[ticker])

# Add GitLab
names.append('GitLab')
x_vals.append(gtlb_rev_growth)
y_vals.append(gtlb_op_margin)
sizes.append(gtlb['market_cap_b'] * 2)
colors.append(TEAL)

# Create figure
fig, ax = plt.subplots(figsize=(14, 10))

# Plot competitors
for i, ticker in enumerate(relevant_comps):
    ax.scatter(x_vals[i], y_vals[i], s=sizes[i], c=[colors[i]], alpha=0.6, 
               edgecolors='white', linewidth=1.5, zorder=3)
    ax.annotate(names[i], (x_vals[i], y_vals[i]), 
                xytext=(8, 8), textcoords='offset points',
                fontsize=10, fontweight='bold', color=colors[i])

# Plot GitLab (larger, highlighted)
ax.scatter(x_vals[-1], y_vals[-1], s=sizes[-1] * 1.5, c=[TEAL], 
           edgecolors='white', linewidth=3, zorder=4)
ax.annotate('GitLab', (x_vals[-1], y_vals[-1]),
            xytext=(10, 10), textcoords='offset points',
            fontsize=13, fontweight='bold', color=TEAL)

# Add EV/Revenue labels
for i, ticker in enumerate(relevant_comps):
    ev_rev = comp_data[ticker]['ev_revenue']
    ax.annotate(f'{ev_rev:.1f}x', (x_vals[i], y_vals[i] - 3),
                xytext=(0, -15), textcoords='offset points',
                fontsize=8, color=colors[i], ha='center', alpha=0.7)

# EV/Revenue for GitLab
ax.annotate(f'{gtlb_ev_rev:.1f}x', (x_vals[-1], y_vals[-1] - 3),
            xytext=(0, -18), textcoords='offset points',
            fontsize=10, color=TEAL, ha='center', fontweight='bold')

# Grid lines
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.3, zorder=1)
ax.axvline(x=0, color='gray', linestyle='--', alpha=0.3, zorder=1)
ax.grid(True, alpha=0.2, linestyle='-')

# Labels
ax.set_xlabel('Revenue Growth (%)', fontsize=14, fontweight='bold')
ax.set_ylabel('Operating Margin (%)', fontsize=14, fontweight='bold')
ax.set_title('GitLab (GTLB) Competitive Position: Growth vs. Margin\n' +
             'Bubble size = Market Cap | EV/Revenue shown below each name\n' +
             'Source: /input/repo/extracted/competitor_data.json',
             fontsize=16, fontweight='bold', pad=20)

# Quadrant labels
ax.text(35, -35, 'High Growth\nLow Margin', fontsize=9, color='gray', ha='center', alpha=0.5)
ax.text(35, 10, 'High Growth\nHigh Margin', fontsize=9, color='gray', ha='center', alpha=0.5)
ax.text(-5, -35, 'Low Growth\nLow Margin', fontsize=9, color='gray', ha='center', alpha=0.5)

plt.tight_layout()
os.makedirs('/workspace/assets/charts', exist_ok=True)
plt.savefig('/workspace/assets/charts/02-competitive-position.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.savefig('/workspace/assets/charts/02-competitive-position.svg', bbox_inches='tight', facecolor='white')
print("Chart 2 saved: 02-competitive-position.png")
