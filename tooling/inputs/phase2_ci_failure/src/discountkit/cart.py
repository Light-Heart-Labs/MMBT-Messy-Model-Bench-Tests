"""Shopping cart with discount support."""
from dataclasses import dataclass
from typing import List, Optional
import json
from .discount import apply_discount


@dataclass
class CartLine:
    sku: str
    qty: int
    unit_price: float


class Cart:
    """A simple cart that totals lines and optionally applies a cart-wide discount."""

    def __init__(self):
        self.lines: List[CartLine] = []
        self._discount_pct: Optional[float] = None

    def add(self, sku: str, qty: int, unit_price: float) -> None:
        self.lines.append(CartLine(sku=sku, qty=qty, unit_price=unit_price))

    def set_discount(self, percent_off: float) -> None:
        self._discount_pct = percent_off

    def subtotal(self) -> float:
        return round(sum(line.qty * line.unit_price for line in self.lines), 2)

    def total(self) -> float:
        sub = self.subtotal()
        if self._discount_pct is None:
            return sub
        return apply_discount(sub, self._discount_pct)

    def line_count(self) -> int:
        return len(self.lines)
