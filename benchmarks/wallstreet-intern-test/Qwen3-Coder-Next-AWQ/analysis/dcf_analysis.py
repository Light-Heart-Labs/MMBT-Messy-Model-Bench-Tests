#!/usr/bin/env python3
"""
DocuSign DCF Analysis
Based on three-statement model and financial projections
"""

import pandas as pd
import numpy as np

# Key assumptions
revenue_growth_rate = 0.08  # 8% revenue growth
operating_margin_target = 0.12  # 12% operating margin
fcf_margin_target = 0.30  # 30% FCF margin
terminal_growth_rate = 0.03  # 3% terminal growth
discount_rate = 0.09  # 9% WACC
shares_outstanding = 200_000_000  # 200M shares

# Base year (FY2026) financials
revenue_2026 = 3219.5  # $3.22B
fcf_2026 = 1058.6  # $1.06B

# Project 5 years
years = list(range(2027, 2032))

# Project revenue
revenue = [revenue_2026 * (1 + revenue_growth_rate)**i for i in range(len(years) + 1)]

# Project FCF
fcf = [revenue[i] * fcf_margin_target for i in range(len(years) + 1)]

# Calculate present value of FCF
pv_fcf = []
for i in range(1, len(years) + 1):
    pv = fcf[i] / (1 + discount_rate)**i
    pv_fcf.append(pv)

# Calculate terminal value
fcf_last = fcf[-1]
terminal_value = (fcf_last * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
pv_terminal = terminal_value / (1 + discount_rate)**len(years)

# Enterprise value
enterprise_value = sum(pv_fcf) + pv_terminal

# Equity value
debt = 185.1  # $185M debt from balance sheet
cash = 618.2  # $618M cash from balance sheet
equity_value = enterprise_value - debt + cash

# Per share value
share_price = equity_value / (shares_outstanding / 1_000_000)

print("=== DocuSign DCF Analysis ===")
print(f"Revenue Growth Rate: {revenue_growth_rate*100}%")
print(f"FCF Margin Target: {fcf_margin_target*100}%")
print(f"Terminal Growth Rate: {terminal_growth_rate*100}%")
print(f"Discount Rate (WACC): {discount_rate*100}%")
print()
print("=== Financial Projections ===")
print(f"{'Year':<10} {'Revenue ($M)':<15} {'FCF ($M)':<15} {'PV FCF ($M)':<15}")
print("-" * 60)
for i, year in enumerate(years):
    print(f"{year:<10} ${revenue[i+1]:<14,.1f} ${fcf[i+1]:<14,.1f} ${pv_fcf[i]:<14,.1f}")

print()
print(f"Terminal Value: ${terminal_value:,.1f}M")
print(f"PV Terminal Value: ${pv_terminal:,.1f}M")
print()
print("=== Valuation ===")
print(f"Enterprise Value: ${enterprise_value:,.1f}M")
print(f"Debt: ${debt:,.1f}M")
print(f"Cash: ${cash:,.1f}M")
print(f"Equity Value: ${equity_value:,.1f}M")
print(f"Shares Outstanding: {shares_outstanding:,}")
print(f"Share Price: ${share_price:.2f}")
print()
print("=== Scenario Analysis ===")

# Bear case (lower growth, lower margins)
bear_revenue_growth = 0.05
bear_fcf_margin = 0.25
bear_revenue = [revenue_2026 * (1 + bear_revenue_growth)**i for i in range(len(years) + 1)]
bear_fcf = [bear_revenue[i] * bear_fcf_margin for i in range(len(years) + 1)]
bear_pv_fcf = [bear_fcf[i] / (1 + discount_rate)**i for i in range(1, len(years) + 1)]
bear_terminal_value = (bear_fcf[-1] * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
bear_pv_terminal = bear_terminal_value / (1 + discount_rate)**len(years)
bear_ev = sum(bear_pv_fcf) + bear_pv_terminal
bear_equity_value = bear_ev - debt + cash
bear_share_price = bear_equity_value / (shares_outstanding / 1_000_000)

# Base case (already calculated)
base_share_price = share_price

# Bull case (higher growth, higher margins)
bull_revenue_growth = 0.10
bull_fcf_margin = 0.35
bull_revenue = [revenue_2026 * (1 + bull_revenue_growth)**i for i in range(len(years) + 1)]
bull_fcf = [bull_revenue[i] * bull_fcf_margin for i in range(len(years) + 1)]
bull_pv_fcf = [bull_fcf[i] / (1 + discount_rate)**i for i in range(1, len(years) + 1)]
bull_terminal_value = (bull_fcf[-1] * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
bull_pv_terminal = bull_terminal_value / (1 + discount_rate)**len(years)
bull_ev = sum(bull_pv_fcf) + bull_pv_terminal
bull_equity_value = bull_ev - debt + cash
bull_share_price = bull_equity_value / (shares_outstanding / 1_000_000)

print(f"Bear Case (5% growth, 25% FCF margin): ${bear_share_price:.2f}")
print(f"Base Case (8% growth, 30% FCF margin): ${base_share_price:.2f}")
print(f"Bull Case (10% growth, 35% FCF margin): ${bull_share_price:.2f}")

# Save results to file
with open('analysis/dcf_analysis_results.txt', 'w') as f:
    f.write("=== DocuSign DCF Analysis Results ===\n\n")
    f.write("Key Assumptions:\n")
    f.write(f"- Revenue Growth Rate: {revenue_growth_rate*100}%\n")
    f.write(f"- FCF Margin Target: {fcf_margin_target*100}%\n")
    f.write(f"- Terminal Growth Rate: {terminal_growth_rate*100}%\n")
    f.write(f"- Discount Rate (WACC): {discount_rate*100}%\n\n")
    f.write("Financial Projections:\n")
    for i, year in enumerate(years):
        f.write(f"{year}: Revenue=${revenue[i+1]:,.1f}M, FCF=${fcf[i+1]:,.1f}M, PV_FCF=${pv_fcf[i]:,.1f}M\n")
    f.write(f"\nTerminal Value: ${terminal_value:,.1f}M\n")
    f.write(f"PV Terminal Value: ${pv_terminal:,.1f}M\n\n")
    f.write("Valuation:\n")
    f.write(f"Enterprise Value: ${enterprise_value:,.1f}M\n")
    f.write(f"Equity Value: ${equity_value:,.1f}M\n")
    f.write(f"Share Price: ${share_price:.2f}\n\n")
    f.write("Scenario Analysis:\n")
    f.write(f"Bear Case: ${bear_share_price:.2f}\n")
    f.write(f"Base Case: ${base_share_price:.2f}\n")
    f.write(f"Bull Case: ${bull_share_price:.2f}\n")

print("\nResults saved to analysis/dcf_analysis_results.txt")
