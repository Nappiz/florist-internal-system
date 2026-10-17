from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException

from models.inventory_balance_model import InventoryBalance
from tests.unit.test_catalogue.base import CatalogueTestCase
from use_cases.inventory.move_stock import move_stock


class MoveStockNumericBoundaryTests(CatalogueTestCase):
    def test_incoming_unit_cost_exceeding_numeric_column_is_rejected_cleanly(self):
        self.db.add(InventoryBalance(material_id=self.material.id))
        self.db.commit()
        with self.assertRaises(HTTPException) as caught:
            move_stock(self.db, self.actor, [{"material_id": self.material.id, "quantity_delta": Decimal("0.000001"), "unit_cost": Decimal("999999999999999000000")}], "purchase_received", uuid4())
        self.assertEqual(caught.exception.status_code, 422)

    def test_valid_large_outflow_uses_sufficient_decimal_precision(self):
        self.db.add(InventoryBalance(material_id=self.material.id, quantity_on_hand=Decimal("100000000000"), average_unit_cost=Decimal("1000000000000000"), has_received_cost=True))
        self.db.commit()
        total = move_stock(self.db, self.actor, [{"material_id": self.material.id, "quantity_delta": Decimal("-100000000000")}], "adjustment", uuid4())
        self.assertEqual(total, Decimal("100000000000000000000000000.00000000"))
        self.assertEqual(self.db.get(InventoryBalance, self.material.id).quantity_on_hand, 0)
