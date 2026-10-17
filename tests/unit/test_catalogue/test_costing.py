from decimal import Decimal

from tests.unit.test_catalogue.base import CatalogueTestCase, InventoryBalance, Product, ProductFlower, ProductMaterial, SupplierMaterial, SupplierStore, flower_recipe, material_cost, product_recipe


class CostingTests(CatalogueTestCase):
    def test_missing_cost_is_unknown(self):
        flower = self.flower()
        cost = flower_recipe(self.db, flower.id)
        self.assertIsNone(cost["estimated_hpp"])
        self.assertFalse(cost["cost_complete"])
        self.assertEqual(cost["cost_sources"][0]["source"], "missing")

    def test_inventory_cost_wins_even_when_stock_is_zero(self):
        self.db.add(InventoryBalance(material_id=self.material.id, quantity_on_hand=0, average_unit_cost=Decimal("12.5"), has_received_cost=True))
        self.db.commit()
        self.assertEqual(material_cost(self.db, self.material.id), {"unit_cost": Decimal("12.5"), "source": "inventory"})

    def test_listing_uses_normalized_price_and_active_supplier(self):
        store = SupplierStore(name="Shop", is_active=True)
        self.db.add(store)
        self.db.flush()
        self.db.add(SupplierMaterial(material_id=self.material.id, supplier_id=store.id, listing_name="Pack", listed_price=1000, package_quantity=1, package_unit="pack", quantity_in_base_unit=100, is_active=True))
        self.db.commit()
        self.assertEqual(material_cost(self.db, self.material.id), {"unit_cost": Decimal("10"), "source": "listing"})
        store.is_active = False
        self.db.commit()
        self.assertIsNone(material_cost(self.db, self.material.id)["unit_cost"])

    def test_recursive_recipe_aggregates_each_explicit_additional_quantity_once(self):
        flower = self.flower()
        self.db.add(InventoryBalance(material_id=self.material.id, quantity_on_hand=20, average_unit_cost=10, has_received_cost=True))
        product = Product(sku="PRD-1", name="Bouquet", selling_price=5000, assembly_labor_cost=50, is_active=True)
        self.db.add(product)
        self.db.flush()
        self.db.add_all([ProductFlower(product_id=product.id, flower_id=flower.id, quantity_required=3), ProductMaterial(product_id=product.id, material_id=self.material.id, quantity_required=1, unit="pcs")])
        self.db.commit()
        cost = product_recipe(self.db, product.id)
        self.assertEqual(cost["materials"], [{"material_id": str(self.material.id), "quantity": Decimal("7"), "unit": "pcs"}])
        self.assertEqual(cost["labor_cost"], Decimal("350"))
        self.assertEqual(cost["estimated_hpp"], Decimal("420"))
        flower.estimated_labor_cost = 900
        self.db.commit()
        self.assertEqual(cost["labor_cost"], Decimal("350"))

