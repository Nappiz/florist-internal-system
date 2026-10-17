from tests.endpoint.endpoint_custom_bouquets.support import BouquetEndpointCase

class CustomOrderTests(BouquetEndpointCase):
    def test_custom_order_finalized_only_no_discount_bypass_and_frozen_snapshot(self):
        draft=self.create_bouquet()
        order_payload={"customer_name":"Buyer","items":[{"custom_bouquet_id":draft["id"],"quantity":2}]}
        self.assertEqual(self.client.post("/bouquet-test/orders",json=order_payload).status_code,409)
        self.client.post(f"/bouquet-test/custom-bouquets/{draft['id']}/finalize",json={})
        self.assertEqual(self.client.post("/bouquet-test/orders",json={**order_payload,"discount_amount":1}).status_code,403)
        response=self.client.post("/bouquet-test/orders",json=order_payload)
        self.assertEqual(response.status_code,201,response.text)
        order=response.json();url=f"/bouquet-test/orders/{order['id']}"
        self.assertEqual(self.client.patch(url,json={"discount_amount":1}).status_code,403)
        self.assertEqual(self.client.patch(url,json={"items":[{"custom_bouquet_id":draft["id"],"unit_price":1}]}).status_code,403)
        response=self.client.post(url+"/confirm",json={})
        self.assertEqual(response.status_code,200,response.text)
        item=response.json()["items"][0]
        self.assertEqual(item["item_type"],"CUSTOM_BOUQUET")
        self.assertEqual(item["recipe_snapshot"]["personalization"]["gift_message"],"Hello")
        self.assertEqual(item["estimated_hpp_snapshot"],"54.00000000")
        from sqlalchemy.orm import Session
        from models.flower_material_model import FlowerMaterial
        from sqlalchemy import select
        with Session(self.engine) as db:
            db.scalar(select(FlowerMaterial)).quantity_required=90
            db.commit()
        self.assertEqual(self.client.get(url).json()["items"][0]["recipe_snapshot"]["materials"][0]["quantity"],"6.000000")

        self.assertEqual(self.client.post(url+"/start-production",json={}).status_code,200)
        response=self.client.post(url+"/complete-production",json={})
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(response.json()["production"]["total_production_cost"],"108.00000000")
        self.assertEqual(self.client.post(url+"/complete-production",json={}).status_code,409)
        from models.inventory_balance_model import InventoryBalance
        from models.inventory_movement_model import InventoryMovement
        from sqlalchemy import func
        from uuid import UUID
        with Session(self.engine) as db:
            self.assertEqual(db.get(InventoryBalance,UUID(self.material_id)).quantity_on_hand,88)
            self.assertEqual(db.scalar(select(func.count()).select_from(InventoryMovement)),1)

    def test_production_rechecks_stock_after_builder_estimate(self):
        row=self.finalized_bouquet()
        response=self.client.post("/bouquet-test/orders",json={"customer_name":"Buyer","items":[{"custom_bouquet_id":row["id"]}]})
        self.assertEqual(response.status_code,201,response.text)
        url=f"/bouquet-test/orders/{response.json()['id']}"
        self.assertEqual(self.client.post(url+"/confirm",json={}).status_code,200)
        self.assertEqual(self.client.post(url+"/start-production",json={}).status_code,200)
        from sqlalchemy.orm import Session
        from models.inventory_balance_model import InventoryBalance
        from uuid import UUID
        with Session(self.engine) as db:
            db.get(InventoryBalance,UUID(self.material_id)).quantity_on_hand=0
            db.commit()
        self.assertEqual(self.client.post(url+"/complete-production",json={}).status_code,409)
        self.assertEqual(self.client.get(url).json()["status"],"in_production")
