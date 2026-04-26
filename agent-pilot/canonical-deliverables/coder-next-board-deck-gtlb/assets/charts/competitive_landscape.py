#!/usr/bin/env python3
"""
Competitive Landscape Chart
Generates: EV/Revenue vs. Revenue Growth scatter plot
"""

import matplotlib.pyplot as plt
import json
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
COLOR_GTLB = '#1E88E5'  # GitLab blue
COLOR_PEER = '#9E9E9E'  # Gray for peers

# Load data
with open('/input/repo/extracted/competitor_data.json', 'r') as f:
    data = json.load(f)

# Extract data for scatter plot
tickers = []
names = []
ev_revenues = []
revenue_growths = []
market_caps = []

for ticker, info in data.items():
    tickers.append(ticker)
    names.append(info['name'])
    ev_revenues.append(info['ev_revenue'])
    revenue_growths.append(info['revenue_growth'] * 100)  # Convert to %
    market_caps.append(info['market_cap_b'])

# Create figure
fig, ax = plt.subplots(figsize=(12, 8))
fig.suptitle('Competitive Landscape: EV/Revenue vs. Revenue Growth', fontsize=16, fontweight='bold')

# Create scatter plot
for i, ticker in enumerate(tickers):
    if ticker == 'GTLB':
        color = COLOR_GTLB
        marker = 'o'
        size = 200
        label = 'GitLab (GTLB)'
    else:
        color = COLOR_PEER
        marker = 's'
        size = 100
        label = None
    
    ax.scatter(revenue_growths[i], ev_revenues[i], 
               c=color, marker=marker, s=size, alpha=0.7, label=label)
    
    # Add ticker label
    ax.annotate(ticker, (revenue_growths[i], ev_revenues[i]), 
                xytext=(5, 5), textcoords='offset points', fontsize=9)

# Add peer average line
peer_ev_rev = sum(ev_revenues[1:]) / (len(ev_revenues) - 1)  # Exclude GitLab
peer_growth = sum(revenue_growths[1:]) / (len(revenue_growths) - 1)  # Exclude GitLab

ax.axhline(y=peer_ev_rev, color='red', linestyle='--', linewidth=1, 
           label=f'Peer Avg EV/Revenue ({peer_ev_rev:.2f}x)')
ax.axvline(x=peer_growth, color='blue', linestyle='--', linewidth=1, 
           label=f'Peer Avg Revenue Growth ({peer_growth:.1f}%)')

# Set labels
ax.set_xlabel('Revenue Growth (%)', fontsize=12)
ax.set_ylabel('EV/Revenue (x)', fontsize=12)
ax.set_title('GitLab vs. Peers (2026E)', fontsize=12)

# Add legend
ax.legend(loc='upper right', fontsize=9)

# Set axis limits
ax.set_xlim(10, 35)
ax.set_ylim(1, 14)

plt.tight_layout()
plt.savefig('/workspace/assets/charts/competitive_landscape.png', dpi=150, 
            bbox_inches='tight', facecolor='#FAFAFA')
plt.close()

print("Competitive landscape chart generated: /workspace/assets/charts/competitive_landscape.png")
