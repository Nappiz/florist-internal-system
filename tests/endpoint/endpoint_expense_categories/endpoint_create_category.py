from tests.helpers.auth import AuthEndpointTestCase
from routes.expense_categories import router
from models.expense_category_model import ExpenseCategory

class CategoryEndpointTest(AuthEndpointTestCase):
    def setUp(self):
        super().setUp()
    def test_staff_cannot_write_and_admin_can_archive(self):
        self.login_as('staff')
        self.assertEqual(self.client.post('/api/v1/expense-categories',json={'name':'Marketing'}).status_code,403)
        self.login_as()
        response=self.client.post('/api/v1/expense-categories',json={'name':'Marketing'})
        self.assertEqual(response.status_code,201,response.text)
        identity=response.json()['id']
        self.assertFalse(self.client.delete(f'/api/v1/expense-categories/{identity}').json()['is_active'])
        self.login_as('staff')
        self.assertEqual(self.client.get('/api/v1/expense-categories').json()['items'],[])
