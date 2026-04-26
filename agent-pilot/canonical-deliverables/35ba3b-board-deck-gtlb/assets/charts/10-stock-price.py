#!/usr/bin/env python3
"""
Chart 10: Stock Price History — 52-Week Range and Current Price
Shows the dramatic decline from highs.

Source data: /input/repo/extracted/historical_prices.csv
Reproduces: Part of Slide 1 (Recommendation)
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

TEAL = '#0D9488'
RED = '#DC2626'
GREEN = '#16A34A'

# Load historical prices
df = pd.read_csv('/input/repo/extracted/historical_prices.csv', parse_dates=['Date'])
dates = df['Date']
closes = df['Close']

fig, ax = plt.subplots(figsize=(14, 6))

# Plot price history
ax.plot(dates, closes, color=TEAL, linewidth=1.5, alpha=0.8)
ax.fill_between(dates, closes, alpha=0.1, color=TEAL)

# Mark key levels
current_price = closes.iloc[-1]
high_52w = closes.max()
low_52w = closes.min()

ax.axhline(y=current_price, color=TEAL, linestyle='-', linewidth=2, alpha=0.8)
ax.axhline(y=high_52w, color=RED, linestyle='--', alpha=0.5, linewidth=1)
ax.axhline(y=low_52w, color=GREEN, linestyle='--', alpha=0.5, linewidth=1)

# Annotations
ax.annotate(f'Current: ${current_price:.2f}', 
            xy=(dates.iloc[-1], current_price), xytext=(dates.iloc[-10], current_price+3),
            fontsize=11, fontweight='bold', color=TEAL,
            arrowprops=dict(arrowstyle='->', color=TEAL, lw=1.5))

high_idx = closes.idxmax()
low_idx = closes.idxmin()
ax.annotate(f'52W High: ${high_52w:.0f}', 
            xy=(high_idx, high_52w), xytext=(dates.iloc[-15], high_52w+3),
            fontsize=10, color=RED, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=RED, lw=1))

ax.annotate(f'52W Low: ${low_52w:.0f}', 
            xy=(low_idx, low_52w), xytext=(dates.iloc[-15], low_52w-5),
            fontsize=10, color=GREEN, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=GREEN, lw=1))

# Calculate decline
decline_pct = (current_price - high_52w) / high_52w * 100
mid_date = dates.iloc[len(dates)//2]
ax.text(mid_date, high_52w * 0.5, f'{decline_pct:.0f}% decline from 52-week high',
        ha='center', fontsize=12, fontweight='bold', color=RED, alpha=0.7)

ax.set_xlabel('Date', fontsize=12, fontweight='bold')
ax.set_ylabel('Price ($)', fontsize=12, fontweight='bold')
ax.set_title('GitLab (GTLB) Stock Price: 52-Week Range\n' +
             'Source: /input/repo/extracted/historical_prices.csv',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.2)

plt.tight_layout()
os.makedirs('/workspace/assets/charts', exist_ok=True)
plt.savefig('/workspace/assets/charts/10-stock-price.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.savefig('/workspace/assets/charts/10-stock-price.svg', bbox_inches='tight', facecolor='white')
print("Chart 10 saved: 10-stock-price.png")
