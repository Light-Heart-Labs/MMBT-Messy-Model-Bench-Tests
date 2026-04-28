"""Discount calculations.

Discounts are expressed as percent-off (0-100). The library used to take
a fraction (0.0-1.0) before v0.3.0; that interface was removed. See
CHANGELOG.md.
"""


def discount_amount(price: float, percent_off: float) -> float:
    """Return the dollar amount discounted from `price` at `percent_off` percent.

    Examples:
        discount_amount(100.0, 20.0) -> 20.0
        discount_amount(40.0, 50.0) -> 20.0
    """
    if percent_off < 0 or percent_off > 100:
        raise ValueError(f"percent_off must be in [0, 100], got {percent_off}")
    return round(price * percent_off, 2)


def apply_discount(price: float, percent_off: float) -> float:
    """Return the price after applying `percent_off` percent discount."""
    return round(price - discount_amount(price, percent_off), 2)
