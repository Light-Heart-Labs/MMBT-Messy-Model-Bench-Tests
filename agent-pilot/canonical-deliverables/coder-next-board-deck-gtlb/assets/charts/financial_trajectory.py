#!/usr/bin/env python3
"""
Financial Trajectory Chart
Generates: historical + projected revenue, margins, FCF
"""

import matplotlib.pyplot as plt
import json
import pandas as pd
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
COLOR_REVENUE = '#1E88E5'  # GitLab blue
COLOR_MARGIN = '#43A047'   # Green
COLOR_FCF = '#E53935'      # Red

# Load data
with open('/input/repo/extracted/financial_summary.json', 'r') as f:
    data = json.load(f)

fy_labels = data['fy_labels']
revenue = data['revenue']
op_margin = data['op_income']  # Will convert to margin
fcf = data['fcf']

# Convert to DataFrame for easier manipulation
df = pd.DataFrame({
    'FY': fy_labels,
    'Revenue': revenue,
    'OpIncome': op_margin,
    'FCF': fcf
})

# Calculate margins
df['Revenue'] = df['Revenue'] / 1000  # Convert to $B
df['OpMargin'] = (df['OpIncome'] / df['Revenue']) * 100
df['FCF'] = df['FCF'] / 1000  # Convert to $B

# Create figure with 3 subplots
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('GitLab Inc. (GTLB) Financial Trajectory', fontsize=16, fontweight='bold')

# Plot 1: Revenue
ax1.plot(df['FY'], df['Revenue'], marker='o', linewidth=2, markersize=8, 
         color=COLOR_REVENUE, label='Revenue')
ax1.set_title('Revenue ($B)', fontsize=12, fontweight='bold')
ax1.set_xlabel('Fiscal Year')
ax1.set_ylabel('Revenue ($B)')
ax1.grid(True, alpha=0.3)
ax1.tick_params(axis='x', rotation=45)

# Add data labels
for i, v in enumerate(df['Revenue']):
    ax1.text(i, v + 0.05, f'${v:.1f}B', ha='center', fontsize=10)

# Plot 2: Operating Margin
ax2.plot(df['FY'], df['OpMargin'], marker='s', linewidth=2, markersize=8, 
         color=COLOR_MARGIN, label='Operating Margin')
ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax2.set_title('Operating Margin (%)', fontsize=12, fontweight='bold')
ax2.set_xlabel('Fiscal Year')
ax2.set_ylabel('Margin (%)')
ax2.grid(True, alpha=0.3)
ax2.tick_params(axis='x', rotation=45)

# Add data labels
for i, v in enumerate(df['OpMargin']):
    ax2.text(i, v + 0.5, f'{v:.1f}%', ha='center', fontsize=10)

# Plot 3: Free Cash Flow
ax3.plot(df['FY'], df['FCF'], marker='^', linewidth=2, markersize=8, 
         color=COLOR_FCF, label='Free Cash Flow')
ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax3.set_title('Free Cash Flow ($B)', fontsize=12, fontweight='bold')
ax3.set_xlabel('Fiscal Year')
ax3.set_ylabel('FCF ($B)')
ax3.grid(True, alpha=0.3)
ax3.tick_params(axis='x', rotation=45)

# Add data labels
for i, v in enumerate(df['FCF']):
    ax3.text(i, v + 0.05, f'${v:.1f}B', ha='center', fontsize=10)

plt.tight_layout()
plt.savefig('/workspace/assets/charts/financial_trajectory.png', dpi=150, 
            bbox_inches='tight', facecolor='#FAFAFA')
plt.close()

print("Financial trajectory chart generated: /workspace/assets/charts/financial_trajectory.png")
