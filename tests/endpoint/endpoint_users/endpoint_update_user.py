from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from models import User
from tests.helpers.auth import AuthEndpointTestCase


class UpdateUserEndpointTests(AuthEndpointTestCase):
    def test_current_password_guesses_are_rate_limited(self):
        self.login_as("staff")
        for _ in range(4):
            response = self.client.patch(f"/users/{self.staff_id}", json={"username": "changed", "current_password": "WrongGuess10@"})
            self.assertEqual(response.status_code, 403)
        blocked = self.client.patch(f"/users/{self.staff_id}", json={"username": "changed", "current_password": "WrongGuess10@"})
        self.assertEqual(blocked.status_code, 429)

    def test_staff_cannot_edit_superadmin_or_other_accounts(self):
        self.login_as("staff")
        self.assertEqual(self.client.patch(f"/users/{self.admin_id}", json={"username": "hacked", "current_password": self.password}).status_code, 403)
        self.assertEqual(self.client.patch(f"/users/{self.staff_id}", json={"is_superadmin": True, "current_password": self.password}).status_code, 422)

    def test_self_edit_requires_current_password_and_revokes_sessions(self):
        self.login_as("staff")
        self.assertEqual(self.client.patch(f"/users/{self.staff_id}", json={"username": "changed"}).status_code, 403)
        self.assertEqual(self.client.patch(f"/users/{self.staff_id}", json={"username": "changed", "current_password": "Incorrect10@"}).status_code, 403)
        response = self.client.patch(f"/users/{self.staff_id}", json={"username": "changed", "password": "Changed10@", "current_password": self.password})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(self.client.get("/auth/me").status_code, 401)
        self.assertEqual(self.client.post("/auth/login", json={"username": "staff", "password": self.password}).status_code, 401)
        self.login_as("changed", "Changed10@")

    def test_superadmin_can_reset_staff_password_and_revoke_existing_sessions(self):
        with TestClient(self.app, base_url="http://localhost", headers={"Origin": self.origin}) as staff_client:
            self.login_as("staff", client=staff_client)
            self.login_as()
            response = self.client.patch(f"/users/{self.staff_id}", json={"password": "ResetStaff10@"})
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(staff_client.get("/auth/me").status_code, 401)
            self.assertEqual(self.client.get("/auth/me").status_code, 200)

    def test_superadmin_protection_survives_username_change(self):
        self.login_as()
        response = self.client.patch(f"/users/{self.admin_id}", json={"username": "owner", "current_password": self.password})
        self.assertEqual(response.status_code, 200, response.text)
        self.login_as("staff")
        self.assertEqual(self.client.patch(f"/users/{self.admin_id}", json={"password": "TakenOver10@"}).status_code, 403)
        with Session(self.engine) as db:
            admin = db.get(User, UUID(self.admin_id))
            self.assertTrue(admin.is_superadmin)
            self.assertEqual(admin.username, "owner")

    def test_rejects_empty_null_weak_duplicate_and_reserved_updates(self):
        self.login_as()
        for data, status in (({}, 422), ({"username": None}, 422), ({"password": "weak"}, 422), ({"username": "SUPERADMIN"}, 409)):
            with self.subTest(data=data):
                self.assertEqual(self.client.patch(f"/users/{self.staff_id}", json=data).status_code, status)
