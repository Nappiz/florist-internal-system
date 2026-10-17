import importlib.util
import unittest
from decimal import Decimal

from fastapi import HTTPException


class CalculateTotalsTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec("use_cases.orders.calculate_totals"), "Order total calculation is not implemented")

    def calculate(self, *args):
        from use_cases.orders.calculate_totals import calculate_totals
        return calculate_totals(*args)

    def test_integer_idr_line_rounding_and_discount_shipping(self):
        self.assertEqual(self.calculate([{"quantity": 3, "unit_price": 12500}], 500, 1000), (37500, 38000))
        self.assertEqual(self.calculate([{"quantity": 1, "unit_price": Decimal("1.5")}], 0, 0), (2, 2))

    def test_negative_total_and_overflow_are_rejected(self):
        for items, discount, shipping in [([{"quantity": 1, "unit_price": 100}], 101, 0), ([{"quantity": 1000000, "unit_price": 999999999999999}], 0, 0)]:
            with self.subTest(items=items), self.assertRaises(HTTPException) as error:
                self.calculate(items, discount, shipping)
            self.assertEqual(error.exception.status_code, 422)
