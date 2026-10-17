from uuid import uuid4
from tests.endpoint.endpoint_orders.support import OrderEndpointCase


class OrderPaymentTests(OrderEndpointCase):
    def test_payments_are_positive_idempotent_and_cannot_overpay_or_mutate_cancelled(self):
        order=self.create_order()
        path=f"/order-test/orders/{order['id']}/payments"
        key=str(uuid4())
        payment={"cash_account_id":self.cash_account_id,"payment_key":key,"amount":10000}
        response=self.client.post(path,json=payment)
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(response.json()["payment_status"],"partial")
        self.assertEqual(self.client.post(path,json=payment).json()["paid_amount"],10000)
        self.assertEqual(self.client.patch(f"/order-test/orders/{order['id']}",json={"discount_amount":20000}).status_code,409)
        self.assertEqual(self.client.post(path,json={**payment,"amount":10001}).status_code,409)
        self.assertEqual(self.client.post(path,json={"cash_account_id":self.cash_account_id,"payment_key":str(uuid4()),"amount":15001}).status_code,409)
        for invalid in ({"amount":1},{"cash_account_id":self.cash_account_id,"payment_key":str(uuid4()),"amount":0},{"cash_account_id":self.cash_account_id,"payment_key":str(uuid4()),"amount":True}):
            self.assertEqual(self.client.post(path,json=invalid).status_code,422)
        self.action(order["id"],"cancel")
        self.assertEqual(self.client.post(path,json={"cash_account_id":self.cash_account_id,"payment_key":str(uuid4()),"amount":1}).status_code,409)
