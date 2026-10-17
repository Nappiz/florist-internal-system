from tests.endpoint.endpoint_custom_bouquets.support import BouquetEndpointCase

class CreateBouquetTests(BouquetEndpointCase):
    def test_staff_builder_security_server_price_and_no_inventory_change(self):
        from sqlalchemy.orm import Session
        from models.inventory_balance_model import InventoryBalance
        from uuid import UUID
        row=self.create_bouquet()
        self.assertEqual(row["proposed_price"],30000)
        self.assertEqual(row["estimated_hpp"],"54.00000000")
        self.assertEqual(row["personalization"]["gift_message"],"Hello")
        for changes in ({"assembly_fee":0},{"final_price":1},{"flowers":[{"flower_id":self.flower_id,"quantity":0}]},{"flowers":[{"flower_id":self.flower_id,"quantity":True}]}):
            response=self.client.post("/bouquet-test/custom-bouquets",json={**self.payload,**changes})
            self.assertEqual(response.status_code,422,response.text)
        with Session(self.engine) as db:
            self.assertEqual(db.get(InventoryBalance,UUID(self.material_id)).quantity_on_hand,100)
        token=self.client.headers.pop("X-CSRF-Token")
        self.assertEqual(self.client.post("/bouquet-test/custom-bouquets",json=self.payload).status_code,403)
        self.client.headers["X-CSRF-Token"]=token
        self.client.post("/auth/logout")
        self.assertEqual(self.client.get("/bouquet-test/custom-bouquets").status_code,401)

    def test_draft_patch_preserves_composition_and_material_requirements_endpoint(self):
        row=self.create_bouquet()
        url=f"/bouquet-test/custom-bouquets/{row['id']}"
        response=self.client.patch(url,json={"name":"Renamed","image_reference":"https://example.com/custom.png"})
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(response.json()["proposed_price"],30000)
        response=self.client.get(url+"/materials")
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(response.json()["materials"][0]["quantity"],"6.000000")
        self.assertEqual(response.json()["availability"],"available")
