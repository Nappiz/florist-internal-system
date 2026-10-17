from uuid import uuid4
from tests.endpoint.endpoint_orders.support import OrderEndpointCase


class CreateOrderTests(OrderEndpointCase):
    def test_draft_totals_validation_auth_and_audit_are_server_controlled(self):
        order = self.create_order(discount_amount=500, shipping_charge=1000)
        self.assertEqual(order["status"], "draft")
        self.assertEqual(order["total_amount"], 25500)
        self.assertEqual(order["payment_status"], "unpaid")
        self.assertEqual(order["created_by"], self.staff_id)
        for changes in ({"items":[]}, {"total_amount":1}, {"status":"ready"}, {"created_by":str(uuid4())}, {"fulfillment_method":"delivery"}, {"discount_amount":999999}):
            with self.subTest(changes=changes):
                response = self.client.post("/order-test/orders", json={"customer_name":"Customer","items":[{"flower_id":self.flower_id,"quantity":1}], **changes})
                self.assertEqual(response.status_code, 422, response.text)
        token=self.client.headers.pop("X-CSRF-Token")
        self.assertEqual(self.client.post("/order-test/orders",json={"customer_name":"Customer","items":[{"flower_id":self.flower_id,"quantity":1}]}).status_code,403)
        self.client.headers["X-CSRF-Token"]=token

    def test_list_filters_pagination_and_draft_item_updates(self):
        first=self.create_order(customer_name="Literal 100%")
        self.create_order(customer_name="Other")
        page=self.client.get("/order-test/orders",params={"q":"%","limit":1}).json()
        self.assertEqual(page["total"],1)
        self.assertEqual(page["items"][0]["id"],first["id"])
        response=self.client.patch(f"/order-test/orders/{first['id']}",json={"items":[{"flower_id":self.flower_id,"quantity":3,"unit_price":100}]})
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(response.json()["total_amount"],300)
        for payload in ({},{"customer_name":None},{"items":None},{"items":[{"quantity":1}]},{"items":[{"flower_id":self.flower_id,"quantity":True}]}):
            self.assertEqual(self.client.patch(f"/order-test/orders/{first['id']}",json=payload).status_code,422)
