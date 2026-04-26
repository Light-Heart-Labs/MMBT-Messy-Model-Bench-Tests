#!/usr/bin/env python3
"""
Chart 8: Confidence & Limitations — Radar Chart
Shows what we're confident about vs. what we're estimating.

Source data: /input/repo/memo/gitlab_investment_memo.md (Confidence and Limitations section)
Reproduces: Slide 12 of the deck
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

TEAL = '#0D9488'
BLUE = '#2563EB'
RED = '#DC2626'
GRAY = '#6B7280'

# Confidence dimensions
categories = [
    'Revenue\nTrajectory',
    'Gross\nMargins',
    'Balance\nSheet',
    'SaaS Model\nQuality',
    'ARR & NRR',
    'AI\nMonetization',
    'Competitive\nDynamics',
]

# Confidence scores (0-10)
confident = [9, 9, 10, 8, 5, 4, 5]  # What we're confident about
estimating = [9, 9, 10, 8, 5, 4, 5]  # Same data, just labeled differently

# Actually, let's split them properly:
# Confident: Revenue, Margins, Balance Sheet, SaaS Model
# Estimating: ARR/NRR, AI Monetization, Competitive Dynamics
confident_scores = [9, 9, 10, 8, 3, 2, 3]
estimating_scores = [1, 1, 0, 2, 7, 8, 7]

# Combine for display
all_scores = [
    max(c, e) for c, e in zip(confident_scores, estimating_scores)
]

n = len(categories)
angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
angles += angles[:1]

# Close the polygon
confident_scores += confident_scores[:1]
estimating_scores += estimating_scores[:1]
all_scores += all_scores[:1]

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

# Plot confident
ax.plot(angles, confident_scores, 'o-', color=TEAL, linewidth=3, label='Confident', zorder=3)
ax.fill(angles, confident_scores, color=TEAL, alpha=0.15, zorder=2)

# Plot estimating
ax.plot(angles, estimating_scores, 'o-', color=RED, linewidth=3, label='Estimating', zorder=3)
ax.fill(angles, estimating_scores, color=RED, alpha=0.15, zorder=2)

# Grid
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=11, fontweight='bold')
ax.set_ylim(0, 10)
ax.set_yticks([2, 4, 6, 8, 10])
ax.set_yticklabels(['2', '4', '6', '8', '10'], fontsize=9, color=GRAY)
ax.grid(True, alpha=0.3)

# Add value labels
for i, (c, e) in enumerate(zip(confident_scores[:-1], estimating_scores[:-1])):
    if c > e:
        ax.text(angles[i], c + 0.5, f'{c}', ha='center', fontsize=9, color=TEAL, fontweight='bold')
    elif e > c:
        ax.text(angles[i], e + 0.5, f'{e}', ha='center', fontsize=9, color=RED, fontweight='bold')
    else:
        ax.text(angles[i], c + 0.5, f'{c}', ha='center', fontsize=9, color=GRAY, fontweight='bold')

# Legend
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=12, framealpha=0.9)

ax.set_title('Confidence Assessment: What We Know vs. What We Estimate\n' +
             'Source: /input/repo/memo/gitlab_investment_memo.md (Confidence and Limitations section)',
             fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
os.makedirs('/workspace/assets/charts', exist_ok=True)
plt.savefig('/workspace/assets/charts/08-confidence-limitations.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.savefig('/workspace/assets/charts/08-confidence-limitations.svg', bbox_inches='tight', facecolor='white')
print("Chart 8 saved: 08-confidence-limitations.png")
