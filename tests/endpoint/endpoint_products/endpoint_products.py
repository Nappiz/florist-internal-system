from fastapi import FastAPI
from fastapi.testclient import TestClient

from configs.auth_dependencies import authenticated_context, csrf_context
from configs.database import get_db
from routes.products import router
from tests.unit.test_catalogue.base import CatalogueTestCase


class ProductEndpointTests(CatalogueTestCase):
    def setUp(self):
        super().setUp()
        app = FastAPI()
        app.include_router(router, prefix="/api/v1")
        app.dependency_overrides[get_db] = lambda: self.db
        app.dependency_overrides[authenticated_context] = lambda: self.actor
        app.dependency_overrides[csrf_context] = lambda: self.actor
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        super().tearDown()

    def test_product_crud_bom_and_cost(self):
        flower = self.flower()
        response = self.client.post("/api/v1/products", json={"sku": "P", "name": "Bouquet", "selling_price": 5000, "bom": {"flowers": [{"flower_id": str(flower.id), "quantity_required": 3}]}})
        self.assertEqual(response.status_code, 201, response.text)
        product_id = response.json()["id"]
        self.assertEqual(response.json()["available_quantity"], 0)
        self.assertEqual(self.client.get(f"/api/v1/products/{product_id}/bom").status_code, 200)
        self.assertEqual(self.client.get(f"/api/v1/products/{product_id}/cost").status_code, 200)
        self.assertEqual(self.client.get("/api/v1/products?q=Bouquet").json()["total"], 1)
        self.assertEqual(self.client.patch(f"/api/v1/products/{product_id}", json={"selling_price": 6000}).status_code, 200)
        self.assertEqual(self.client.put(f"/api/v1/products/{product_id}/bom", json={"materials": [{"material_id": str(self.material.id), "quantity_required": 2, "unit": "pcs"}]}).status_code, 200)
        self.assertEqual(self.client.delete(f"/api/v1/products/{product_id}").status_code, 204)
        self.assertFalse(self.client.get(f"/api/v1/products/{product_id}").json()["is_active"])

    def test_nested_product_and_archived_flower_rejected(self):
        flower = self.flower()
        flower.is_active = False
        self.db.commit()
        for bom, expected in [({"products": []}, 422), ({"flowers": [{"flower_id": str(flower.id), "quantity_required": 1}]}, 409)]:
            response = self.client.post("/api/v1/products", json={"sku": "P", "name": "Bouquet", "selling_price": 1000, "bom": bom})
            self.assertEqual(response.status_code, expected, response.text)
