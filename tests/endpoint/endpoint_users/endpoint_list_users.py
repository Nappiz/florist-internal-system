from tests.helpers.auth import AuthEndpointTestCase


class ListUsersEndpointTests(AuthEndpointTestCase):
    def test_list_requires_superadmin_and_is_paginated(self):
        self.assertEqual(self.client.get("/users").status_code, 401)
        self.login_as("staff")
        self.assertEqual(self.client.get("/users").status_code, 403)
        self.login_as()
        response = self.client.get("/users?limit=1&offset=0")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertNotIn("password_hash", response.text)
        self.assertEqual(self.client.get("/users?limit=101").status_code, 422)
        self.assertEqual(self.client.get("/users?offset=" + str(10**30)).status_code, 422)
