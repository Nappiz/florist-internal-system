import unittest
from decimal import Decimal

from fastapi import HTTPException

from use_cases.expenses.calculate_expense import calculate_expense


class CalculateExpenseTests(unittest.TestCase):
    def test_decimal_totals_and_shipping_discount(self):
        subtotal, total = calculate_expense(3, Decimal("0.10"), Decimal("0.20"), Decimal("0.05"))
        self.assertEqual(subtotal, Decimal("0.30"))
        self.assertEqual(total, Decimal("0.45"))

    def test_zero_total_is_valid_but_negative_and_overflow_are_rejected(self):
        self.assertEqual(calculate_expense(2, Decimal("100"), Decimal("10"), Decimal("210"))[1], Decimal("0.00"))
        for values in [(2, Decimal("100"), Decimal("0"), Decimal("201")),
                       (1000000, Decimal("999999999999.99"), Decimal("999999999999.99"), Decimal("0"))]:
            with self.subTest(values=values), self.assertRaises(HTTPException) as error:
                calculate_expense(*values)
            self.assertEqual(error.exception.status_code, 422)
