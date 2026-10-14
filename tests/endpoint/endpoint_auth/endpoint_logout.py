from tests.helpers.auth import AuthEndpointTestCase


class LogoutEndpointTests(AuthEndpointTestCase):
    def test_logout_revokes_captured_session_token(self):
        self.login_as("staff")
        token = self.client.cookies.get("florist_session")
        self.assertEqual(self.client.post("/auth/logout").status_code, 204)
        self.client.cookies.set("florist_session", token)
        self.assertEqual(self.client.get("/auth/me").status_code, 401)

    def test_logout_rejects_missing_csrf_and_foreign_origin(self):
        self.login_as("staff")
        self.client.headers.pop("X-CSRF-Token")
        self.assertEqual(self.client.post("/auth/logout").status_code, 403)
        self.assertEqual(self.client.get("/auth/me").status_code, 200)
        self.login_as("staff")
        self.assertEqual(self.client.post("/auth/logout", headers={"Origin": "https://evil.example"}).status_code, 403)
