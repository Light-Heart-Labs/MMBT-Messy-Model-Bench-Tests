from discountkit import discount_amount, apply_discount


def test_discount_amount():
    # 20% off $100 should be $20
    assert discount_amount(100.0, 20.0) == 20.0
    # 50% off $40 should be $20
    assert discount_amount(40.0, 50.0) == 20.0
    # 0% off any price is 0
    assert discount_amount(99.99, 0) == 0


def test_apply_discount():
    # $100 with 20% off → $80
    assert apply_discount(100.0, 20.0) == 80.0
    # $40 with 50% off → $20
    assert apply_discount(40.0, 50.0) == 20.0
    # $99.99 with 0% off → unchanged
    assert apply_discount(99.99, 0.0) == 99.99


def test_discount_amount_validates_range():
    import pytest
    with pytest.raises(ValueError):
        discount_amount(100.0, -1.0)
    with pytest.raises(ValueError):
        discount_amount(100.0, 101.0)
