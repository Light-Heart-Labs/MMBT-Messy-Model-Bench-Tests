#!/usr/bin/env python3
"""
Chart 5: Risk Assessment — Probability vs. Impact Matrix
Prioritized risk visualization with bubble sizes.

Source data: /input/repo/memo/gitlab_investment_memo.md (Risk Assessment section)
Reproduces: Slide 7 of the deck
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

TEAL = '#0D9488'
RED = '#DC2626'
ORANGE = '#F59E0B'
YELLOW = '#EAB308'
BLUE = '#2563EB'
GREEN = '#16A34A'

# Risk data: (name, probability, impact, size, color)
risks = [
    ('NRR Decline\n< 110%', 0.7, 0.9, 0.9, RED),
    ('GitHub Copilot\nCompetition', 0.6, 0.8, 0.8, ORANGE),
    ('Macro Downturn', 0.5, 0.8, 0.7, YELLOW),
    ('AI Monetization\nFailure', 0.4, 0.7, 0.6, YELLOW),
    ('Open-Source\nCannibalization', 0.3, 0.6, 0.5, BLUE),
    ('Key Person\nRisk', 0.2, 0.5, 0.4, GREEN),
]

fig, ax = plt.subplots(figsize=(12, 10))

# Plot risks
for name, prob, impact, size, color in risks:
    ax.scatter(prob * 100, impact * 100, s=size * 2000, c=[color], alpha=0.6,
               edgecolors='white', linewidth=2, zorder=5)
    ax.annotate(name, (prob * 100, impact * 100),
                xytext=(10, 10), textcoords='offset points',
                fontsize=11, fontweight='bold', color=color)

# Quadrant labels
ax.text(75, 95, 'HIGH PROBABILITY\nHIGH IMPACT', fontsize=12, fontweight='bold', 
        color=RED, ha='center', alpha=0.5)
ax.text(25, 95, 'LOW PROBABILITY\nHIGH IMPACT', fontsize=12, fontweight='bold',
        color=BLUE, ha='center', alpha=0.5)
ax.text(75, 25, 'HIGH PROBABILITY\nLOW IMPACT', fontsize=12, fontweight='bold',
        color=ORANGE, ha='center', alpha=0.5)
ax.text(25, 25, 'LOW PROBABILITY\nLOW IMPACT', fontsize=12, fontweight='bold',
        color=GREEN, ha='center', alpha=0.5)

# Grid
ax.axhline(y=50, color='gray', linestyle='--', alpha=0.3)
ax.axvline(x=50, color='gray', linestyle='--', alpha=0.3)
ax.grid(True, alpha=0.15)

# Labels
ax.set_xlabel('Probability (%)', fontsize=14, fontweight='bold')
ax.set_ylabel('Impact (%)', fontsize=14, fontweight='bold')
ax.set_title('GitLab (GTLB) Risk Assessment: Probability vs. Impact\n' +
             'Bubble size = overall risk score | Color = risk category',
             fontsize=15, fontweight='bold', pad=20)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)

plt.tight_layout()
os.makedirs('/workspace/assets/charts', exist_ok=True)
plt.savefig('/workspace/assets/charts/05-risk-matrix.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.savefig('/workspace/assets/charts/05-risk-matrix.svg', bbox_inches='tight', facecolor='white')
print("Chart 5 saved: 05-risk-matrix.png")
