from decimal import Decimal

from fastapi import HTTPException

from tests.unit.test_catalogue.base import CatalogueTestCase, InventoryBalance
from schemas.product_schema import ProductCreate, ProductBOM
from use_cases.products.create_product import create_product
from use_cases.products.get_product import get_product
from use_cases.products.replace_bom import replace_bom


class ProductAvailabilityTests(CatalogueTestCase):
    def test_availability_floors_aggregated_material_requirements(self):
        flower = self.flower(quantity="2.5")
        self.db.add(InventoryBalance(material_id=self.material.id, quantity_on_hand=Decimal("20.9"), average_unit_cost=10, has_received_cost=True))
        self.db.commit()
        product = create_product(self.db, self.actor, ProductCreate(sku="P", name="Bouquet", selling_price=5000, bom={"flowers": [{"flower_id": flower.id, "quantity_required": 3}], "materials": [{"material_id": self.material.id, "quantity_required": 1, "unit": "pcs"}]}))
        self.assertEqual(product["available_quantity"], 2)
        self.assertEqual(product["estimated_hpp"], Decimal("385"))
        self.assertEqual(product["estimated_profit"], Decimal("4615"))
        self.material.is_active = False
        self.db.commit()
        self.assertEqual(get_product(self.db, product["id"])["available_quantity"], 0)

    def test_empty_active_recipe_rejected_without_losing_old_recipe(self):
        flower = self.flower()
        product = create_product(self.db, self.actor, ProductCreate(sku="P", name="Bouquet", selling_price=5000, bom={"flowers": [{"flower_id": flower.id, "quantity_required": 1}]}))
        with self.assertRaises(HTTPException):
            replace_bom(self.db, self.actor, product["id"], ProductBOM())
        self.assertEqual(get_product(self.db, product["id"])["name"], "Bouquet")
