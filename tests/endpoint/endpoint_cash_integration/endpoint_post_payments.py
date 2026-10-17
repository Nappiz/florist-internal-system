from datetime import date
from uuid import uuid4
from sqlalchemy import select,func
from sqlalchemy.orm import Session
from tests.endpoint.endpoint_orders.support import OrderEndpointCase
from models import OrderPayment,CashTransaction,PurchasePayment

class PaymentCashIntegrationTests(OrderEndpointCase):
    def count(self,model):
        with Session(self.engine) as db:return db.scalar(select(func.count()).select_from(model))

    def test_order_retry_cash_movement_and_refund_are_consistent(self):
        order=self.create_order()
        path="/api/v1/orders/"+order['id']
        payload={'payment_key':str(uuid4()),'cash_account_id':self.cash_account_id,'amount':10000}
        for _ in range(2):
            response=self.client.post(path+'/payments',json=payload)
            self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(self.count(OrderPayment),1)
        self.assertEqual(self.count(CashTransaction),1)
        self.assertEqual(self.client.get('/api/v1/cashflow/summary').status_code,403)
        self.login_as('superadmin')
        summary=self.client.get('/api/v1/cashflow/summary').json()
        self.assertEqual(summary['cash_in'],10000)
        with Session(self.engine) as db:identity=str(db.scalar(select(CashTransaction.id)))
        reverse={'operation_key':str(uuid4()),'transaction_date':date.today().isoformat(),'reason':'Payment entered twice outside system'}
        for _ in range(2):
            response=self.client.post('/api/v1/cashflow/transactions/'+identity+'/reverse',json=reverse)
            self.assertEqual(response.status_code,201,response.text)
        self.assertEqual(self.count(CashTransaction),2)
        detail=self.client.get(path).json()
        self.assertEqual(detail['paid_amount'],0)
        self.assertEqual(detail['payment_status'],'unpaid')
        self.assertIsNotNone(detail['payments'][0]['reversed_at'])
        self.assertEqual(self.client.get('/api/v1/cashflow/summary').json()['closing_balance'],0)
        self.assertTrue(self.client.get('/api/v1/cashflow/reconciliation').json()['is_reconciled'])

    def test_invalid_account_rolls_back_payment_and_status(self):
        order=self.create_order()
        path='/api/v1/orders/'+order['id']
        response=self.client.post(path+'/payments',json={'payment_key':str(uuid4()),'cash_account_id':str(uuid4()),'amount':1000})
        self.assertEqual(response.status_code,404,response.text)
        self.assertEqual(self.count(OrderPayment),0)
        self.assertEqual(self.count(CashTransaction),0)
        self.assertEqual(self.client.get(path).json()['paid_amount'],0)
        self.assertEqual(self.client.post(path+'/payments',json={'payment_key':str(uuid4()),'amount':1000}).status_code,422)

    def test_purchase_receipt_has_no_cash_out_until_payment(self):
        store=self.client.post('/api/v1/suppliers',json={'name':'Finance test supplier','platform':'offline'}).json()
        purchase=self.client.post('/api/v1/purchases',json={'supplier_id':store['id'],'purchase_date':'2026-10-01','items':[{'material_id':self.material_id,'quantity':'5','unit_price':100}]}).json()
        path='/api/v1/purchases/'+purchase['id']
        for action in ['order','receive']:
            response=self.client.post(path+'/'+action)
            self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(self.count(CashTransaction),0)
        body={'payment_key':str(uuid4()),'cash_account_id':self.cash_account_id,'payment_date':'2026-10-01','amount':250}
        first=self.client.post(path+'/payments',json=body)
        self.assertEqual(first.status_code,201,first.text)
        self.assertEqual(first.json()['payment_status'],'partial')
        self.assertEqual(self.client.post(path+'/payments',json=body).status_code,201)
        self.assertEqual(self.count(PurchasePayment),1)
        self.assertEqual(self.count(CashTransaction),1)
        self.login_as('superadmin')
        summary=self.client.get('/api/v1/cashflow/summary').json()
        self.assertEqual(summary['cash_out'],250)
        self.assertEqual(summary['closing_balance'],-250)
        self.assertTrue(self.client.get('/api/v1/cashflow/reconciliation').json()['is_reconciled'])

    def test_validated_historical_mapping_backfills_exactly_once(self):
        order=self.create_order()
        with Session(self.engine) as db:
            from uuid import UUID
            old=OrderPayment(order_id=UUID(order['id']),payment_key=uuid4(),payment_date=date(2026,10,1),amount=100)
            db.add(old);db.commit();identity=str(old.id)
        self.login_as('superadmin')
        self.assertEqual(self.client.get('/api/v1/cashflow/reconciliation').json()['issue_counts']['unmapped_payment'],1)
        body={'operation_key':str(uuid4()),'reason':'Validated bank statement','mappings':[{'source_type':'order_payment','payment_id':identity,'cash_account_id':self.cash_account_id}]}
        for _ in range(2):
            response=self.client.post('/api/v1/cashflow/backfill',json=body)
            self.assertEqual(response.status_code,201,response.text)
        self.assertEqual(self.count(CashTransaction),1)
        self.assertEqual(self.client.get('/api/v1/cashflow/summary').json()['cash_in'],100)
        self.assertTrue(self.client.get('/api/v1/cashflow/reconciliation').json()['is_reconciled'])
