from tests.helpers.auth import AuthEndpointTestCase


class UserStatusEndpointTests(AuthEndpointTestCase):
    def test_only_superadmin_can_change_status_and_final_admin_is_protected(self):
        path = f"/users/{self.staff_id}/status"
        self.assertEqual(self.client.patch(path, json={"is_active": False}).status_code, 401)
        self.login_as("staff")
        self.assertEqual(self.client.patch(path, json={"is_active": False}).status_code, 403)
        self.login_as()
        response = self.client.patch(path, json={"is_active": False})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertFalse(response.json()["is_active"])
        self.assertEqual(self.client.patch(f"/users/{self.admin_id}/status", json={"is_active": False}).status_code, 403)
        self.assertEqual(self.client.patch(path, json={"is_active": True, "role": "superadmin"}).status_code, 422)
        self.assertEqual(self.client.patch(path, json={}).status_code, 422)
        response = self.client.patch(path, json={"is_active": True})
        self.assertEqual(response.status_code, 200, response.text)
        self.login_as("staff")
