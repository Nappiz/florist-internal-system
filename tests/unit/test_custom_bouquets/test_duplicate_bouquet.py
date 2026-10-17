import importlib.util
import unittest
from fastapi import HTTPException

class DuplicateBouquetTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec("use_cases.custom_bouquets"), "Custom bouquet lifecycle is missing")
        from tests.unit.test_custom_bouquets.support import setup_bouquet
        setup_bouquet(self)

    def test_finalize_immutable_duplicate_reprices(self):
        from use_cases.custom_bouquets.create_bouquet import create_bouquet
        from use_cases.custom_bouquets.finalize_bouquet import finalize_bouquet
        from use_cases.custom_bouquets.update_bouquet import update_bouquet
        from use_cases.custom_bouquets.duplicate_bouquet import duplicate_bouquet
        from schemas.custom_bouquet_schema import BouquetFinalize
        row=create_bouquet(self.db,self.staff,self.data)
        row=finalize_bouquet(self.db,self.staff,row.id,BouquetFinalize())
        self.assertEqual(row.status,"finalized")
        self.flower.selling_price=20000
        self.db.commit()
        with self.assertRaises(HTTPException): update_bouquet(self.db,self.staff,row.id,self.data)
        copied=duplicate_bouquet(self.db,self.staff,row.id)
        self.assertEqual(copied.status,"draft")
        self.assertEqual(copied.proposed_price,61100)
        self.assertEqual(row.final_price,31100)
        self.assertEqual(row.personalization["gift_message"],"Hello")
