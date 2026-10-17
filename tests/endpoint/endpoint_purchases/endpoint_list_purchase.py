from tests.helpers.catalogue import CatalogueEndpointTestCase


class PurchaseListTests(CatalogueEndpointTestCase):
    def test_list_includes_material_names(self):
        supplier = self.supplier()
        red = self.material(sku="PC-RED", name="Pipe cleaner red")
        white = self.material(sku="PC-WHITE", name="Pipe cleaner white")
        red_listing = self.listing(red, supplier, listing_name="Red bundle")
        white_listing = self.listing(white, supplier, listing_name="White bundle")

        created = self.client.post(
            "/api/v1/purchases",
            json={
                "supplier_id": supplier["id"],
                "purchase_date": "2026-10-01",
                "items": [
                    {"material_id": red["id"], "supplier_listing_id": red_listing["id"], "quantity": "1"},
                    {"material_id": white["id"], "supplier_listing_id": white_listing["id"], "quantity": "1"},
                ],
            },
        )
        self.assertEqual(created.status_code, 201, created.text)

        page = self.client.get("/api/v1/purchases").json()
        purchase = next(item for item in page["items"] if item["id"] == created.json()["id"])

        self.assertCountEqual(purchase["item_names"], ["Pipe cleaner red", "Pipe cleaner white"])
