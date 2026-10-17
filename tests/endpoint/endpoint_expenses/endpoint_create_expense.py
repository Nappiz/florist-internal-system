from uuid import uuid4
from tests.helpers.expenses import ExpenseEndpointTestCase


class LegacyCreateExpenseTests(ExpenseEndpointTestCase):
    def test_retired_writer_requires_login_then_returns_gone(self):
        path='/expenses'+('' if 'create'=='create' else '/'+str(uuid4()))
        self.assertEqual(self.client.post(path).status_code,401)
        self.login_as('staff')
        self.assertEqual(self.client.post(path).status_code,410)

    def test_retired_writer_requires_csrf(self):
        self.login_as()
        self.client.headers.pop('X-CSRF-Token')
        path='/expenses'+('' if 'create'=='create' else '/'+str(uuid4()))
        self.assertEqual(self.client.post(path).status_code,403)
