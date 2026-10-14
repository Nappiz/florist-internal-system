from tests.helpers.auth import AuthEndpointTestCase


class GetUserEndpointTests(AuthEndpointTestCase):
    def test_staff_can_read_only_own_account(self):
        self.login_as("staff")
        self.assertEqual(self.client.get(f"/users/{self.staff_id}").status_code, 200)
        self.assertEqual(self.client.get(f"/users/{self.admin_id}").status_code, 403)
