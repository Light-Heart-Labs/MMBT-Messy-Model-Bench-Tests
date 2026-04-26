#!/usr/bin/env python3
"""
Chart 7: Confidence & Limitations Spectrum
Source data: /input/repo/memo/gitlab_investment_memo.md (Confidence and Limitations section)
Output: /assets/charts/07_confidence_spectrum.png

Visualizes what we're confident about vs. what we're estimating vs. what a human would do differently.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(12, 8))

BG_COLOR = '#F8FAFC'
ax.set_facecolor(BG_COLOR)
fig.patch.set_facecolor('white')

# Three categories
categories = [
    {
        'title': 'CONFIDENT\n(Fact-based)',
        'items': [
            'Revenue trajectory\n(5 years of data)',
            'Gross margins\n(87-90% stable)',
            'Balance sheet\n($1.26B cash)',
            'SaaS model quality\n(Subscription revenue)',
        ],
        'color': '#059669',
        'x': 0.15,
    },
    {
        'title': 'ESTIMATING\n(Model-based)',
        'items': [
            'ARR & NRR\n(Management metrics)',
            'AI monetization\n(Forward-looking)',
            'Competitive dynamics\n(Unpredictable pace)',
            'FCF margin trajectory\n(Projection)',
        ],
        'color': '#D97706',
        'x': 0.50,
    },
    {
        'title': 'HUMAN WOULD\nDO DIFFERENTLY',
        'items': [
            'Read full 10-K filings\n(SEC blocked us)',
            'Attend earnings calls\n(Live participation)',
            'Customer interviews\n(Validate NRR)',
            'Product evaluation\n(Hands-on testing)',
            'Management meetings\n(Direct conversations)',
        ],
        'color': '#64748B',
        'x': 0.85,
    },
]

y_start = 0.85
y_step = 0.14

for cat in categories:
    # Column header
    ax.add_patch(plt.Rectangle((cat['x'] - 0.12, y_start + 0.05), 0.24, 0.08,
                                facecolor=cat['color'], edgecolor='white',
                                linewidth=2, alpha=0.9, zorder=3))
    ax.text(cat['x'], y_start + 0.09, cat['title'],
            fontsize=10, ha='center', va='center', fontweight='bold', color='white', zorder=4)

    # Items
    for i, item in enumerate(cat['items']):
        y = y_start - i * y_step
        ax.add_patch(plt.Rectangle((cat['x'] - 0.12, y - 0.04), 0.24, 0.08,
                                    facecolor=cat['color'], edgecolor='white',
                                    linewidth=1, alpha=0.3, zorder=2))
        ax.text(cat['x'], y, item,
                fontsize=8, ha='center', va='center', color='#1E293B', zorder=3)

# Confidence arrow
ax.annotate('', xy=(0.95, 0.5), xytext=(0.05, 0.5),
            arrowprops=dict(arrowstyle='<->', color='#475569', lw=2))
ax.text(0.5, 0.45, 'Confidence Level →', fontsize=11, ha='center',
        fontweight='bold', color='#475569')

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
ax.set_title('Confidence & Limitations Spectrum\nGitLab Inc. (GTLB)',
             fontsize=14, fontweight='bold', pad=15)

plt.tight_layout()
plt.savefig('/workspace/assets/charts/07_confidence_spectrum.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Chart 7 saved: 07_confidence_spectrum.png")
