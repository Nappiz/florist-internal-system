from uuid import uuid4
from tests.helpers.auth import AuthEndpointTestCase


class CashAccountEndpointTests(AuthEndpointTestCase):
    def data(self):
        return {'operation_key': str(uuid4()), 'name': '=SUM(1,1)', 'account_type': 'bank', 'opening_balance': 1200, 'opening_date': '2026-01-01', 'reason': 'Verified statement'}

    def test_finance_is_private_and_options_expose_no_balances_to_staff(self):
        self.assertEqual(self.client.get('/api/v1/cash-accounts').status_code, 401)
        self.login_as('staff')
        for path in ('cash-accounts', 'cashflow/summary', 'cashflow/transactions', 'cashflow/breakdown', 'cashflow/export', 'cashflow/reconciliation'):
            self.assertEqual(self.client.get('/api/v1/' + path).status_code, 403, path)
        self.assertEqual(self.client.post('/api/v1/cash-accounts', json=self.data()).status_code, 403)
        options = self.client.get('/api/v1/cash-accounts/options?is_active=false&limit=1')
        self.assertEqual(options.status_code, 200, options.text)
        self.assertEqual(set(options.json()['items'][0]), {'id', 'name', 'account_type'})

    def test_opening_is_idempotent_immutable_and_csrf_protected(self):
        self.login_as()
        data = self.data()
        first = self.client.post('/api/v1/cash-accounts', json=data)
        self.assertEqual(first.status_code, 201, first.text)
        retry = self.client.post('/api/v1/cash-accounts', json=data)
        self.assertEqual(first.json()['id'], retry.json()['id'])
        self.assertEqual(first.json()['balance'], 1200)
        self.assertEqual(self.client.patch('/api/v1/cash-accounts/' + first.json()['id'], json={'operation_key': str(uuid4()), 'opening_balance': 5000, 'reason': 'Invalid edit'}).status_code, 422)
        self.client.headers.pop('X-CSRF-Token')
        self.assertEqual(self.client.post('/api/v1/cash-accounts', json=self.data()).status_code, 403)
