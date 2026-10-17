import importlib.util
import unittest
from fastapi import HTTPException

class CustomOrderSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec("use_cases.custom_bouquets"), "Custom bouquet lifecycle is missing")
        from tests.unit.test_custom_bouquets.support import setup_bouquet
        setup_bouquet(self)

    def test_order_snapshot_has_aggregated_recipe_personalization_and_staff_cannot_override(self):
        from use_cases.custom_bouquets.create_bouquet import create_bouquet
        from use_cases.custom_bouquets.finalize_bouquet import finalize_bouquet
        from schemas.custom_bouquet_schema import BouquetFinalize
        from schemas.order_schema import OrderItemInput
        from use_cases.orders.build_items import build_items
        from use_cases.orders.snapshot_order import snapshot_order,material_changes
        from uuid import uuid4
        row=create_bouquet(self.db,self.staff,self.data)
        finalize_bouquet(self.db,self.staff,row.id,BouquetFinalize())
        items=build_items(self.db,uuid4(),[OrderItemInput(custom_bouquet_id=row.id,quantity=2)],actor=self.staff)
        snapshot_order(self.db,items)
        self.assertEqual(items[0].item_type,"CUSTOM_BOUQUET")
        self.assertEqual(items[0].recipe_snapshot["personalization"]["gift_message"],"Hello")
        self.assertEqual(material_changes(items)[0]["quantity_delta"],-20)
        with self.assertRaises(HTTPException) as error:
            build_items(self.db,uuid4(),[OrderItemInput(custom_bouquet_id=row.id,unit_price=1)],actor=self.staff)
        self.assertEqual(error.exception.status_code,403)
        with self.assertRaises(HTTPException):
            build_items(self.db,uuid4(),[OrderItemInput(custom_bouquet_id=row.id)],actor=self.staff,discount_amount=1)
