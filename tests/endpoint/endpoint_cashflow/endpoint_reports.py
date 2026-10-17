from uuid import uuid4
from tests.helpers.auth import AuthEndpointTestCase


class CashReportEndpointTests(AuthEndpointTestCase):
    def setUp(self):
        super().setUp()
        self.login_as()
        result = self.client.post('/api/v1/cash-accounts', json={'operation_key': str(uuid4()), 'name': '=SUM(1,1)', 'account_type': 'cash', 'opening_date': '2026-01-01', 'opening_balance': 1000, 'reason': 'Actual opening'})
        self.assertEqual(result.status_code, 201, result.text)
        self.first = result.json()['id']

    def test_transfer_summary_and_paginated_running_balance_and_csv(self):
        data = {'operation_key': str(uuid4()), 'from_account_id': self.first, 'to_account_id': self.cash_account_id, 'transaction_date': '2026-01-02', 'amount': 400, 'reason': '@external link'}
        result = self.client.post('/api/v1/cashflow/transfers', json=data)
        self.assertEqual(result.status_code, 201, result.text)
        self.assertEqual(len(result.json()['transactions']), 2)
        self.assertEqual(self.client.post('/api/v1/cashflow/transfers', json=data).json(), result.json())
        period = '?date_from=2026-01-02&date_to=2026-01-02'
        report = self.client.get('/api/v1/cashflow/summary' + period).json()
        self.assertEqual((report['opening_balance'], report['cash_in'], report['cash_out'], report['closing_balance']), (1000, 0, 0, 1000))
        rows = self.client.get('/api/v1/cashflow/transactions' + period + '&cash_account_id=' + self.first + '&limit=1').json()
        self.assertEqual(rows['total'], 1)
        self.assertEqual(rows['items'][0]['running_balance'], 600)
        csv = self.client.get('/api/v1/cashflow/export' + period)
        self.assertEqual(csv.status_code, 200, csv.text)
        self.assertIn("'=SUM(1,1)", csv.text)
        self.assertIn("'@external link", csv.text)
        self.assertIn('attachment;', csv.headers['content-disposition'])
        self.assertEqual(self.client.get('/api/v1/cashflow/summary?date_from=2026-01-02&date_to=2026-01-01').status_code, 422)

    def test_adjustment_requires_reason_and_retries_do_not_duplicate(self):
        data = {'operation_key': str(uuid4()), 'cash_account_id': self.first, 'transaction_date': '2026-01-02', 'amount': 200, 'direction': 'OUT', 'category': 'owner_withdrawal', 'reason': 'Verified owner withdrawal'}
        result = self.client.post('/api/v1/cashflow/adjustments', json=data)
        self.assertEqual(result.status_code, 201, result.text)
        self.assertEqual(self.client.post('/api/v1/cashflow/adjustments', json=data).json(), result.json())
        self.assertEqual(self.client.post('/api/v1/cashflow/adjustments', json=data | {'amount': 300}).status_code, 409)
        self.assertEqual(self.client.post('/api/v1/cashflow/adjustments', json=data | {'operation_key': str(uuid4()), 'reason': ' '}).status_code, 422)
        self.assertEqual(self.client.post('/api/v1/cashflow/transfers', json={'operation_key': str(uuid4()), 'from_account_id': self.first, 'to_account_id': str(uuid4()), 'transaction_date': '2026-01-02', 'amount': 100, 'reason': 'Missing target'}).status_code, 404)
        result = self.client.get('/api/v1/cashflow/summary').json()
        self.assertEqual(result['closing_balance'], 800)
