import unittest
from fastapi import HTTPException
from tests.unit.test_custom_bouquets.support import setup_bouquet
from use_cases.custom_bouquets.create_bouquet import create_bouquet
from use_cases.custom_bouquets.finalize_bouquet import finalize_bouquet
from use_cases.orders.create_order import create_order
from use_cases.orders.update_order import update_order
from schemas.custom_bouquet_schema import BouquetFinalize
from schemas.order_schema import OrderCreate,OrderUpdate,OrderItemInput

class CustomDraftEditTests(unittest.TestCase):
    def setUp(self):
        setup_bouquet(self)
        config=create_bouquet(self.db,self.staff,self.data)
        finalize_bouquet(self.db,self.staff,config.id,BouquetFinalize())
        self.order=create_order(self.db,self.admin,OrderCreate(customer_name='Discount customer',discount_amount=100,price_override_reason='Approved customer quote',items=[OrderItemInput(custom_bouquet_id=config.id)]))

    def test_unrelated_edit_preserves_previously_authorized_discount(self):
        for actor in [self.staff,self.admin]:
            result=update_order(self.db,actor,self.order.id,OrderUpdate(notes='Pickup at 3pm'))
            self.assertEqual(result.notes,'Pickup at 3pm')
            self.assertEqual(result.discount_amount,100)
        with self.assertRaises(HTTPException) as caught:
            update_order(self.db,self.staff,self.order.id,OrderUpdate(discount_amount=101))
        self.assertEqual(caught.exception.status_code,403)

    def test_custom_item_initial_cost_is_available_before_confirmation(self):
        item=self.order.items[0]
        self.assertIsNotNone(item.estimated_hpp_snapshot)
        self.assertTrue(item.cost_complete)
        self.assertEqual(item.labor_cost_snapshot,50)
