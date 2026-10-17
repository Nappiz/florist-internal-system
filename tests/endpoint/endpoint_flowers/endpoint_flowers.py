from fastapi import FastAPI
from fastapi.testclient import TestClient

from configs.auth_dependencies import authenticated_context, csrf_context
from configs.database import get_db
from routes.flowers import router
from tests.unit.test_catalogue.base import CatalogueTestCase


class FlowerEndpointTests(CatalogueTestCase):
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

    def test_create_bom_cost_update_archive_flow(self):
        response = self.client.post("/api/v1/flowers", json={"sku": "F", "name": "Tulip", "selling_price": 1000, "bom": {"materials": [{"material_id": str(self.material.id), "quantity_required": "2", "unit": "pcs"}]}})
        self.assertEqual(response.status_code, 201, response.text)
        flower_id = response.json()["id"]
        self.assertIsNone(response.json()["estimated_hpp"])
        self.assertEqual(self.client.get(f"/api/v1/flowers/{flower_id}/bom").json()["materials"][0]["quantity_required"], "2.000000")
        cost = self.client.get(f"/api/v1/flowers/{flower_id}/cost")
        self.assertEqual(cost.status_code, 200)
        self.assertFalse(cost.json()["cost_complete"])
        self.assertEqual(self.client.patch(f"/api/v1/flowers/{flower_id}", json={"name": "Red tulip"}).status_code, 200)
        self.assertEqual(self.client.get("/api/v1/flowers").json()["total"], 1)
        self.assertEqual(self.client.delete(f"/api/v1/flowers/{flower_id}").status_code, 204)
        self.assertFalse(self.client.get(f"/api/v1/flowers/{flower_id}").json()["is_active"])

    def test_invalid_shape_and_precision_rejected(self):
        for changes in [{"estimated_hpp": 0}, {"selling_price": "1.5"}, {"image_url": "javascript:alert(1)"}, {"bom": {"materials": [{"material_id": str(self.material.id), "quantity_required": "0.0000001", "unit": "pcs"}]}}]:
            response = self.client.post("/api/v1/flowers", json={"sku": "F", "name": "Tulip", "selling_price": 1000, **changes})
            self.assertEqual(response.status_code, 422, response.text)

