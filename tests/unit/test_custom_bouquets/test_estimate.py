import importlib.util
import unittest
from decimal import Decimal
from fastapi import HTTPException

class EstimateTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec("use_cases.custom_bouquets"), "Custom builder server pricing is not implemented")
        from tests.unit.test_custom_bouquets.support import setup_bouquet
        setup_bouquet(self)

    def test_aggregates_flower_option_extra_materials_and_trusted_fees(self):
        from use_cases.custom_bouquets.estimate import estimate
        result = estimate(self.db, self.data)
        self.assertEqual(result["proposed_price"], 31100)
        self.assertEqual(result["estimated_hpp"], Decimal("90"))
        self.assertEqual(result["materials"][0]["quantity"], Decimal("10"))
        self.assertEqual(result["materials"][0]["shortage_quantity"], Decimal("3"))
        self.assertEqual(result["availability"], "insufficient_stock")
        self.assertEqual(result["stem_count"], 3)
        self.assertEqual(len(result["flowers"]), 1)
        self.assertEqual(self.db.get(self.balance_model,self.material.id).quantity_on_hand, Decimal("7"))

    def test_missing_cost_and_mapping_are_explicit(self):
        from use_cases.custom_bouquets.estimate import estimate
        balance = self.db.get(self.balance_model,self.material.id)
        balance.has_received_cost=False
        self.db.flush()
        result=estimate(self.db,self.data)
        self.assertFalse(result["cost_complete"])
        self.assertIsNone(result["estimated_hpp"])
        self.assertEqual(result["availability"], "unknown")

    def test_admin_stem_bounds_apply_to_aggregate(self):
        from use_cases.custom_bouquets.estimate import estimate
        self.settings.max_stems=2
        self.db.flush()
        with self.assertRaises(HTTPException) as error: estimate(self.db,self.data)
        self.assertEqual(error.exception.status_code,422)
