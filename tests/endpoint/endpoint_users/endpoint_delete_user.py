from tests.helpers.auth import AuthEndpointTestCase


class DeleteUserEndpointTests(AuthEndpointTestCase):
    def test_staff_cannot_delete_any_user_and_superadmin_cannot_be_deleted(self):
        self.login_as("staff")
        self.assertEqual(self.client.delete(f"/users/{self.staff_id}").status_code, 403)
        self.assertEqual(self.client.delete(f"/users/{self.admin_id}").status_code, 403)
        self.login_as()
        self.assertEqual(self.client.delete(f"/users/{self.admin_id}").status_code, 403)

    def test_superadmin_can_delete_staff(self):
        self.login_as()
        self.assertEqual(self.client.delete(f"/users/{self.staff_id}").status_code, 204)
        self.assertEqual(self.client.get(f"/users/{self.staff_id}").status_code, 404)
