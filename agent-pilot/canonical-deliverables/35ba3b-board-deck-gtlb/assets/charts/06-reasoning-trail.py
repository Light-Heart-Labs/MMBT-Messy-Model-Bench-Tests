#!/usr/bin/env python3
"""
Chart 6: Reasoning Trail — Dependency Graph
Shows how the agent moved from filings → analysis → conclusion.

Source data: /input/repo/decisions/, /input/repo/research/, /input/repo/memo/
Reproduces: Slide 10 of the deck
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

TEAL = '#0D9488'
BLUE = '#2563EB'
RED = '#DC2626'
GREEN = '#16A34A'
ORANGE = '#F59E0B'
PURPLE = '#8B5CF6'
GRAY = '#6B7280'
LIGHT_BLUE = '#DBEAFE'
LIGHT_GREEN = '#D1FAE5'
LIGHT_RED = '#FEE2E2'
LIGHT_YELLOW = '#FEF3C7'

fig, ax = plt.subplots(figsize=(16, 12))

# Node positions (x, y)
nodes = {
    # Data sources (left column)
    'SEC Filings\n(403 blocked)': (0.05, 0.9),
    'yfinance\nFinancial Data': (0.05, 0.7),
    'Earnings Call\nTranscripts': (0.05, 0.5),
    'Competitor\nData': (0.05, 0.3),
    'Historical\nPrices': (0.05, 0.1),
    
    # Analysis (middle-left)
    'Revenue\nAnalysis': (0.25, 0.8),
    'Margin\nAnalysis': (0.25, 0.6),
    'SaaS Metrics\n(ARR, NRR)': (0.25, 0.4),
    'Competitive\nAnalysis': (0.25, 0.2),
    
    # Decisions (middle)
    'ADR-001:\nCompany Selection': (0.45, 0.85),
    'ADR-002:\nCompetitor Selection': (0.45, 0.65),
    'ADR-003:\nValuation Method': (0.45, 0.45),
    
    # Model (middle-right)
    'Three-Statement\nModel': (0.65, 0.75),
    'DCF\nValuation': (0.65, 0.55),
    'Peer\nComparison': (0.65, 0.35),
    'Scenario\nAnalysis': (0.65, 0.15),
    
    # Dead ends (bottom)
    'SEC 403\nBlocked': (0.45, 0.1),
    'CIK\nConfusion': (0.25, 0.05),
    'DNS\nFailed': (0.65, 0.05),
    
    # Conclusion (right)
    'Investment\nMemo': (0.85, 0.7),
    'BUY\n$42 Target': (0.95, 0.5),
}

# Node colors
node_colors = {
    'SEC Filings\n(403 blocked)': LIGHT_RED,
    'yfinance\nFinancial Data': LIGHT_BLUE,
    'Earnings Call\nTranscripts': LIGHT_GREEN,
    'Competitor\nData': LIGHT_YELLOW,
    'Historical\nPrices': LIGHT_BLUE,
    'Revenue\nAnalysis': LIGHT_BLUE,
    'Margin\nAnalysis': LIGHT_BLUE,
    'SaaS Metrics\n(ARR, NRR)': LIGHT_GREEN,
    'Competitive\nAnalysis': LIGHT_YELLOW,
    'ADR-001:\nCompany Selection': LIGHT_GREEN,
    'ADR-002:\nCompetitor Selection': LIGHT_YELLOW,
    'ADR-003:\nValuation Method': LIGHT_BLUE,
    'Three-Statement\nModel': LIGHT_BLUE,
    'DCF\nValuation': LIGHT_GREEN,
    'Peer\nComparison': LIGHT_YELLOW,
    'Scenario\nAnalysis': LIGHT_BLUE,
    'SEC 403\nBlocked': LIGHT_RED,
    'CIK\nConfusion': LIGHT_RED,
    'DNS\nFailed': LIGHT_RED,
    'Investment\nMemo': LIGHT_GREEN,
    'BUY\n$42 Target': LIGHT_GREEN,
}

# Draw nodes
for name, (x, y) in nodes.items():
    color = node_colors[name]
    ax.add_patch(plt.Rectangle((x-0.06, y-0.04), 0.12, 0.08, 
                                facecolor=color, edgecolor='black', 
                                linewidth=1.5, zorder=3))
    ax.text(x, y, name, ha='center', va='center', fontsize=8, 
            fontweight='bold', zorder=4)

# Edges (data flow)
edges = [
    # Data sources → Analysis
    ('yfinance\nFinancial Data', 'Revenue\nAnalysis'),
    ('yfinance\nFinancial Data', 'Margin\nAnalysis'),
    ('Earnings Call\nTranscripts', 'SaaS Metrics\n(ARR, NRR)'),
    ('Competitor\nData', 'Competitive\nAnalysis'),
    ('Historical\nPrices', 'Competitive\nAnalysis'),
    
    # Analysis → Decisions
    ('Revenue\nAnalysis', 'ADR-001:\nCompany Selection'),
    ('Competitive\nAnalysis', 'ADR-002:\nCompetitor Selection'),
    ('Margin\nAnalysis', 'ADR-003:\nValuation Method'),
    
    # Decisions → Model
    ('ADR-001:\nCompany Selection', 'Three-Statement\nModel'),
    ('ADR-002:\nCompetitor Selection', 'Peer\nComparison'),
    ('ADR-003:\nValuation Method', 'DCF\nValuation'),
    
    # Model → Scenarios
    ('Three-Statement\nModel', 'DCF\nValuation'),
    ('Three-Statement\nModel', 'Scenario\nAnalysis'),
    ('DCF\nValuation', 'Scenario\nAnalysis'),
    ('Peer\nComparison', 'Scenario\nAnalysis'),
    
    # Model → Conclusion
    ('DCF\nValuation', 'Investment\nMemo'),
    ('Peer\nComparison', 'Investment\nMemo'),
    ('Scenario\nAnalysis', 'Investment\nMemo'),
    ('SaaS Metrics\n(ARR, NRR)', 'Investment\nMemo'),
    
    # Dead ends
    ('SEC Filings\n(403 blocked)', 'SEC 403\nBlocked'),
    ('SEC Filings\n(403 blocked)', 'CIK\nConfusion'),
    ('Earnings Call\nTranscripts', 'DNS\nFailed'),
]

for src, dst in edges:
    x1, y1 = nodes[src]
    x2, y2 = nodes[dst]
    ax.annotate('', xy=(x2-0.06, y2), xytext=(x1+0.06, y1),
                arrowprops=dict(arrowstyle='->', color='gray', 
                               lw=1.5, alpha=0.6), zorder=1)

# Title
ax.set_title('Agent Reasoning Trail: From Data Sources to Investment Recommendation\n' +
             'Each node represents a decision point or data artifact. Edges show data flow.\n' +
             'Source: /input/repo/decisions/, /input/repo/research/, /input/repo/memo/',
             fontsize=16, fontweight='bold', pad=20)

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

plt.tight_layout()
os.makedirs('/workspace/assets/charts', exist_ok=True)
plt.savefig('/workspace/assets/charts/06-reasoning-trail.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.savefig('/workspace/assets/charts/06-reasoning-trail.svg', bbox_inches='tight', facecolor='white')
print("Chart 6 saved: 06-reasoning-trail.png")
