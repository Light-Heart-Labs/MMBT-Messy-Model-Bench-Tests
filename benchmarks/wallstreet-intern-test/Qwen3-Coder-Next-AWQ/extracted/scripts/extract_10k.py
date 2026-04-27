#!/usr/bin/env python3
"""
Extract key financial data from DocuSign 10-K filing
"""

import re
from bs4 import BeautifulSoup

def extract_revenue(html_content):
    """Extract total revenue from 10-K"""
    # Look for revenue figures in the HTML
    patterns = [
        r'Total Revenue.*?([\$\d,\.]+)',
        r'Revenue.*?([\$\d,\.]+)',
        r'Net Revenue.*?([\$\d,\.]+)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        if matches:
            return matches[0]
    
    return None

def extract_operating_income(html_content):
    """Extract operating income from 10-K"""
    patterns = [
        r'Operating Income.*?([\$\d,\.]+)',
        r'Income from Operations.*?([\$\d,\.]+)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        if matches:
            return matches[0]
    
    return None

def extract_net_income(html_content):
    """Extract net income from 10-K"""
    patterns = [
        r'Net Income.*?([\$\d,\.]+)',
        r'Net Income Loss.*?([\$\d,\.]+)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        if matches:
            return matches[0]
    
    return None

def extract_free_cash_flow(html_content):
    """Extract free cash flow from 10-K"""
    patterns = [
        r'Free Cash Flow.*?([\$\d,\.]+)',
        r'Cash Flow Operations.*?([\$\d,\.]+)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        if matches:
            return matches[0]
    
    return None

# Read the 10-K file
with open('raw/filings/10-K_20260318_full.html', 'r') as f:
    html_content = f.read()

# Extract key metrics
revenue = extract_revenue(html_content)
operating_income = extract_operating_income(html_content)
net_income = extract_net_income(html_content)
free_cash_flow = extract_free_cash_flow(html_content)

print("=== Extracted Financial Data from 10-K ===")
print(f"Total Revenue: {revenue}")
print(f"Operating Income: {operating_income}")
print(f"Net Income: {net_income}")
print(f"Free Cash Flow: {free_cash_flow}")

# Save extracted data
with open('extracted/10-K_fy2026_metrics.txt', 'w') as f:
    f.write(f"Total Revenue: {revenue}\n")
    f.write(f"Operating Income: {operating_income}\n")
    f.write(f"Net Income: {net_income}\n")
    f.write(f"Free Cash Flow: {free_cash_flow}\n")

print("\nExtracted data saved to extracted/10-K_fy2026_metrics.txt")
