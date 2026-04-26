#!/usr/bin/env python3
"""
Chart 7: Dead Ends — Hypotheses Investigated and Rejected
Shows the agent's failed approaches and what was learned.

Source data: /input/repo/research/dead-ends.md
Reproduces: Slide 11 of the deck
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

RED = '#DC2626'
ORANGE = '#F59E0B'
YELLOW = '#EAB308'
GRAY = '#6B7280'
TEAL = '#0D9488'

# Dead end data from /input/repo/research/dead-ends.md
dead_ends = [
    ('SEC Filing\nDownloads', 'SEC.gov returned 403\nfor all automated\nrequests', 'Used yfinance\ninstead', 0.8, RED),
    ('GitLab IR\nWebsite', 'DNS resolution\nfailed for\ninvestors.gitlab.com', 'No official\npresentations', 0.6, ORANGE),
    ('PRNewswire\nPress Releases', 'Search URL\nreturned 404', 'No press\nreleases', 0.5, ORANGE),
    ('Initial CIK\nLookup', 'Wrong CIK\n(0001687226)\n→ Harper James P', 'Found correct\nCIK 0001653482', 0.7, YELLOW),
    ('Earnings Call\nAudio', 'Seeking Alpha\nrequires JS\nexecution', 'Used text\ntranscripts', 0.4, YELLOW),
]

fig, ax = plt.subplots(figsize=(14, 8))

# Create horizontal bar chart showing severity
y_pos = list(range(len(dead_ends)))
severity = [d[4] for d in dead_ends]
labels = [d[0] for d in dead_ends]
descriptions = [d[1] for d in dead_ends]
resolutions = [d[2] for d in dead_ends]

bars = ax.barh(y_pos, [s * 100 for s in severity], 
               color=[d[4] for d in dead_ends], alpha=0.7, 
               edgecolor='white', linewidth=1.5)

# Add labels and descriptions
for i, (bar, label, desc, res) in enumerate(zip(bars, labels, descriptions, resolutions)):
    width = bar.get_width()
    ax.text(width + 1, bar.get_y() + bar.get_height()/2,
            f'{label}', va='center', ha='left', fontsize=11, fontweight='bold')
    ax.text(width + 1, bar.get_y() + bar.get_height()/2 - 0.15,
            f'{desc}', va='center', ha='left', fontsize=8, color=GRAY)
    ax.text(width + 1, bar.get_y() + bar.get_height()/2 + 0.15,
            f'→ {res}', va='center', ha='left', fontsize=8, color=TEAL, fontweight='bold')

ax.set_yticks(y_pos)
ax.set_yticklabels(labels)
ax.set_xlabel('Impact on Analysis (Severity)', fontsize=12, fontweight='bold')
ax.set_title('Dead Ends: Hypotheses Investigated and Rejected\n' +
             'Source: /input/repo/research/dead-ends.md\n' +
             'Each dead end represents a failed approach that was documented and resolved',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xlim(0, 100)
ax.grid(True, alpha=0.2, axis='x')

plt.tight_layout()
os.makedirs('/workspace/assets/charts', exist_ok=True)
plt.savefig('/workspace/assets/charts/07-dead-ends.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.savefig('/workspace/assets/charts/07-dead-ends.svg', bbox_inches='tight', facecolor='white')
print("Chart 7 saved: 07-dead-ends.png")
