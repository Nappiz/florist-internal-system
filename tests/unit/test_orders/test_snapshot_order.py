import unittest
from decimal import Decimal

from fastapi import HTTPException

from use_cases.orders import snapshot_order


class SnapshotCostTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(callable(getattr(snapshot_order, "snapshot_cost", None)), "Snapshot costs require explicit precision and bounds")

    def test_cost_rounds_half_up_to_eight_places_and_preserves_unknown(self):
        self.assertEqual(snapshot_order.snapshot_cost(Decimal("1.000000005")), Decimal("1.00000001"))
        self.assertIsNone(snapshot_order.snapshot_cost(None))

    def test_nonfinite_negative_and_overflow_are_rejected_before_database_write(self):
        for amount in (Decimal("NaN"), Decimal("Infinity"), Decimal("-1"), Decimal("1e30"), Decimal("999999999999999999999999999999.999999999")):
            with self.subTest(amount=amount), self.assertRaises(HTTPException) as error:
                snapshot_order.snapshot_cost(amount)
            self.assertEqual(error.exception.status_code, 422)
