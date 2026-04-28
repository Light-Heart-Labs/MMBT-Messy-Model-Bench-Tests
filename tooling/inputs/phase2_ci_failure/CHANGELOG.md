# Changelog

## v0.3.1 (current — CI red)

CI is failing on this version. See `ci_failure.log` for the full output.

## v0.3.0

- **BREAKING**: `discount_amount()` and `apply_discount()` now take percent (0-100)
  instead of fraction (0.0-1.0). Update callers from `apply_discount(p, 0.2)` to
  `apply_discount(p, 20.0)`.
- `Cart.line_count()` now returns the number of lines, not the total quantity
  across lines. Tests should be updated where they relied on the old behavior.

## v0.2.0

- Added `Cart.set_discount()` for cart-wide discounts.
- `Cart.line_count()` returns total quantity across lines.

## v0.1.0

- Initial release.
