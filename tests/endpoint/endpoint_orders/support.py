import importlib.util
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from tests.helpers.auth import AuthEndpointTestCase


class OrderEndpointCase(AuthEndpointTestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec("routes.orders"), "Orders endpoints are not implemented")
        super().setUp()
        from routes.orders import router
        self.app.include_router(router, prefix="/order-test")
        self.login_as("staff")
        from models.material_model import Material
        from models.inventory_balance_model import InventoryBalance
        with Session(self.engine) as db:
            material = Material(sku="ORD-M", name="Order material", base_unit="pcs", minimum_stock=0)
            db.add(material)
            db.flush()
            db.add(InventoryBalance(material_id=material.id))
            db.commit()
            self.material_id = str(material.id)
        response = self.client.post("/api/v1/flowers", json={"sku":"ORD-F", "name":"Order flower", "selling_price":12500,"estimated_labor_cost":500,"bom":{"materials":[{"material_id":self.material_id,"quantity_required":"2","unit":"pcs"}]}})
        self.assertEqual(response.status_code, 201, response.text)
        self.flower_id = response.json()["id"]

    def create_order(self, **changes):
        data = {"customer_name":"Customer", "items":[{"flower_id":self.flower_id,"quantity":2}]}
        data.update(changes)
        response = self.client.post("/order-test/orders", json=data)
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def action(self, order_id, action, expected=200, payload=None):
        response = self.client.post(f"/order-test/orders/{order_id}/{action}", json=payload or {})
        self.assertEqual(response.status_code, expected, response.text)
        return response
