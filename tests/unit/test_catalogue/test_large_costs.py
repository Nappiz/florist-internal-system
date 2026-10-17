from decimal import Decimal, localcontext

from models.inventory_balance_model import InventoryBalance
from tests.unit.test_catalogue.base import CatalogueTestCase
from use_cases.flowers.get_flower import get_flower


class LargeCostTests(CatalogueTestCase):
    def test_large_supported_cost_calculates_margin_without_decimal_overflow(self):
        flower = self.flower(quantity="999999999999", labor=0)
        cost = Decimal("9999999999999999.12345678")
        self.db.add(InventoryBalance(material_id=self.material.id, average_unit_cost=cost, quantity_on_hand=0, has_received_cost=True))
        self.db.commit()
        # SQLite stores Numeric through floating point, so assert against the
        # actual retrieved persisted value rather than assuming PostgreSQL precision.
        actual_cost = self.db.get(InventoryBalance, self.material.id).average_unit_cost
        with localcontext() as context:
            context.prec = 80
            expected = Decimal("999999999999") * actual_cost
        response = get_flower(self.db, flower.id)
        self.assertEqual(response["estimated_hpp"], expected)
        self.assertIsNotNone(response["estimated_margin"])
