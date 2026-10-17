from uuid import uuid4

from tests.helpers.expenses import ExpenseEndpointTestCase


class GetExpenseEndpointTests(ExpenseEndpointTestCase):
    def test_detail_requires_login_and_is_shared_with_authenticated_staff(self):
        self.assertEqual(self.client.get(f"/expenses/{uuid4()}").status_code, 401)
        self.login_as()
        record = self.create_expense(self.create_record()["id"])
        self.login_as("staff")
        response = self.client.get(f"/expenses/{record['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["created_by"], self.admin_id)
        self.assertEqual(self.client.get(f"/expenses/{uuid4()}").status_code, 404)
