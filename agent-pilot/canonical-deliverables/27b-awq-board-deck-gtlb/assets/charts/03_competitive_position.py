#!/usr/bin/env python3
"""
Chart 3: Competitive Position — Growth vs. EV/Revenue Scatter
Source data: /input/repo/extracted/competitor_data.json
Output: /assets/charts/03_competitive_position.png

Shows GitLab's position relative to peers on growth vs. valuation.
GitLab should appear as high-growth, low-multiple = mispricing opportunity.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Data from /input/repo/extracted/competitor_data.json
comps = [
    {'ticker': 'GTLB', 'name': 'GitLab', 'ev_rev': 2.56, 'growth': 23.2, 'mc': 3.66},
    {'ticker': 'TEAM', 'name': 'Atlassian', 'ev_rev': 3.22, 'growth': 23.3, 'mc': 18.87},
    {'ticker': 'DDOG', 'name': 'Datadog', 'ev_rev': 12.39, 'growth': 29.2, 'mc': 45.82},
    {'ticker': 'MDB',  'name': 'MongoDB', 'ev_rev': 7.33, 'growth': 26.7, 'mc': 20.38},
    {'ticker': 'CFLT', 'name': 'Confluent', 'ev_rev': 8.69, 'growth': 20.5, 'mc': 11.13},
    {'ticker': 'SNOW', 'name': 'Snowflake', 'ev_rev': 10.07, 'growth': 30.1, 'mc': 48.51},
    {'ticker': 'ZS',   'name': 'Zscaler', 'ev_rev': 6.71, 'growth': 25.9, 'mc': 21.79},
    {'ticker': 'OKTA', 'name': 'Okta', 'ev_rev': 3.88, 'growth': 11.6, 'mc': 13.44},
    {'ticker': 'BILL', 'name': 'Bill.com', 'ev_rev': 2.14, 'growth': 14.4, 'mc': 3.68},
]

GTLB_COLOR = '#2563EB'
COMP_COLOR = '#94A3B8'
BG_COLOR = '#F8FAFC'

fig, ax = plt.subplots(figsize=(10, 7))
ax.set_facecolor(BG_COLOR)
fig.patch.set_facecolor('white')

# Plot peers
for c in comps:
    if c['ticker'] == 'GTLB':
        continue
    size = max(50, min(300, c['mc'] * 5))
    ax.scatter(c['growth'], c['ev_rev'], s=size, color=COMP_COLOR,
               alpha=0.6, edgecolors='white', linewidth=1.5, zorder=2)
    ax.annotate(c['name'], (c['growth'], c['ev_rev']),
                fontsize=8, ha='center', va='bottom', color='#475569')

# Plot GitLab prominently
gtlb = [c for c in comps if c['ticker'] == 'GTLB'][0]
size = max(50, min(300, gtlb['mc'] * 5))
ax.scatter(gtlb['growth'], gtlb['ev_rev'], s=size * 1.5, color=GTLB_COLOR,
           alpha=0.9, edgecolors='white', linewidth=2, zorder=3)
ax.annotate('GitLab (GTLB)', (gtlb['growth'], gtlb['ev_rev']),
            fontsize=11, ha='center', va='bottom', fontweight='bold', color=GTLB_COLOR)

# Peer average line
peer_avg_ev = np.mean([c['ev_rev'] for c in comps if c['ticker'] != 'GTLB'])
ax.axhline(y=peer_avg_ev, color='#DC2626', linestyle='--', linewidth=1.5, alpha=0.6, label=f'Peer Avg EV/Rev: {peer_avg_ev:.1f}x')

ax.set_xlabel('Revenue Growth (%)', fontsize=12, fontweight='bold')
ax.set_ylabel('EV / Revenue (x)', fontsize=12, fontweight='bold')
ax.set_title('Competitive Position: Growth vs. Valuation\nGitLab trades at a significant discount to peers',
             fontsize=14, fontweight='bold', pad=15)

ax.grid(True, alpha=0.2, linestyle='--')

for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)

ax.text(5, 11, 'High Growth\nHigh Multiple', fontsize=9, ha='center', color='#64748B', alpha=0.5)
ax.text(5, 1.5, 'High Growth\nLow Multiple\n← Opportunity', fontsize=9, ha='center', color=GTLB_COLOR, alpha=0.7, fontweight='bold')

ax.set_xlim(5, 35)
ax.set_ylim(0, 14)

plt.tight_layout()
plt.savefig('/workspace/assets/charts/03_competitive_position.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Chart 3 saved: 03_competitive_position.png")
