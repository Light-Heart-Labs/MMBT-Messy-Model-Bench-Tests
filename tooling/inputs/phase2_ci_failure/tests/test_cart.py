from discountkit import Cart


def test_cart_subtotal():
    c = Cart()
    c.add("SKU-A", qty=2, unit_price=10.0)
    c.add("SKU-B", qty=1, unit_price=5.0)
    assert c.subtotal() == 25.0


def test_cart_total_no_discount():
    c = Cart()
    c.add("SKU-A", qty=2, unit_price=10.0)
    assert c.total() == 20.0


def test_cart_total_with_discount():
    c = Cart()
    c.add("SKU-A", qty=2, unit_price=10.0)
    c.add("SKU-B", qty=1, unit_price=5.0)
    c.set_discount(10.0)  # 10% off
    # 10% off $25 = $22.50
    assert c.total() == 22.50


def test_line_count_matches_qty_sum():
    """line_count returns the total quantity across all lines."""
    c = Cart()
    c.add("SKU-A", qty=2, unit_price=10.0)
    c.add("SKU-B", qty=3, unit_price=5.0)
    # Two lines, total qty = 5
    assert c.line_count() == 5
