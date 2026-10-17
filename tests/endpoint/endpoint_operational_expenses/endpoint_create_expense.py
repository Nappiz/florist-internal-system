from tests.helpers.operational_expense_endpoint import OperationalExpenseEndpointTestCase
from datetime import date

class ExpenseEndpointTest(OperationalExpenseEndpointTestCase):
    def test_staff_draft_scope_and_final_permissions(self):
        self.login_as('staff')
        response=self.client.post('/api/v1/expenses',json={'category_id':self.category,'title':'Ads','expense_date':date.today().isoformat(),'amount':100})
        self.assertEqual(response.status_code,201,response.text)
        identity=response.json()['id']
        self.assertEqual(self.client.post(f'/api/v1/expenses/{identity}/post').status_code,403)
        self.assertEqual(self.client.get('/api/v1/expenses/summary').status_code,403)
        self.login_as()
        self.assertEqual(self.client.post(f'/api/v1/expenses/{identity}/post').status_code,200)
        self.login_as('staff')
        own=self.client.get(f'/api/v1/expenses/{identity}')
        self.assertEqual(own.status_code,200,own.text)
        self.assertEqual(own.json()['status'],'posted')
        self.assertEqual(self.client.get('/api/v1/expenses?status=posted').json()['total'],1)
        self.assertEqual(self.client.patch(f'/api/v1/expenses/{identity}',json={'amount':99}).status_code,409)
        self.assertEqual(self.client.delete(f'/api/v1/expenses/{identity}').status_code,409)
        self.login_as('superadmin')
        another=self.client.post('/api/v1/expenses',json={'category_id':self.category,'title':'Private owner expense','expense_date':date.today().isoformat(),'amount':1}).json()['id']
        self.login_as('staff')
        self.assertEqual(self.client.get(f'/api/v1/expenses/{another}').status_code,404)

    def test_web_proof_payment_url_is_stored_and_exact_retry_safe(self):
        from uuid import uuid4
        created=self.client.post('/api/v1/expenses',json={'category_id':self.category,'title':'Ads invoice','expense_date':'2026-10-01','amount':100})
        self.assertEqual(created.status_code,201,created.text)
        path='/api/v1/expenses/'+created.json()['id']
        self.assertEqual(self.client.post(path+'/post').status_code,200)
        payload={'payment_key':str(uuid4()),'cash_account_id':self.cash_account_id,'payment_date':'2026-10-01','amount':100,'method':'bank','proof_url':'https://example.com/proof.pdf'}
        for _ in range(2):
            response=self.client.post(path+'/payments',json=payload)
            self.assertEqual(response.status_code,201,response.text)
            self.assertEqual(response.json()['payment_status'],'paid')
            self.assertEqual(len(response.json()['payments']),1)
            self.assertEqual(response.json()['payments'][0]['proof_url'],payload['proof_url'])
