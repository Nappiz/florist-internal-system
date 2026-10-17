from uuid import uuid4
from tests.helpers.expenses import ExpenseEndpointTestCase


class LegacyUpdateExpenseTests(ExpenseEndpointTestCase):
    def test_retired_writer_requires_login_then_returns_gone(self):
        path='/expenses'+('' if 'update'=='create' else '/'+str(uuid4()))
        self.assertEqual(self.client.patch(path).status_code,401)
        self.login_as('staff')
        self.assertEqual(self.client.patch(path).status_code,410)

    def test_retired_writer_requires_csrf(self):
        self.login_as()
        self.client.headers.pop('X-CSRF-Token')
        path='/expenses'+('' if 'update'=='create' else '/'+str(uuid4()))
        self.assertEqual(self.client.patch(path).status_code,403)
