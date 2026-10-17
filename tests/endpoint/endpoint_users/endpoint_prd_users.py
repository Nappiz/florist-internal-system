from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from models import User
from tests.helpers.auth import AuthEndpointTestCase


class PrdUsersEndpointTests(AuthEndpointTestCase):
    def create_account(self, username="secondadmin", role="superadmin", email="second@example.com"):
        return self.client.post("/users", json={"username": username, "password": self.password,
            "full_name": "Second Owner", "email": email, "role": role})

    def test_create_requires_profile_and_enforces_case_insensitive_email(self):
        self.login_as()
        self.assertEqual(self.client.post("/users", json={"username": "incomplete", "password": self.password}).status_code, 422)
        response = self.create_account()
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["role"], "superadmin")
        self.assertTrue(response.json()["is_superadmin"])
        self.assertEqual(self.create_account("duplicate", "staff", "SECOND@example.com").status_code, 409)

    def test_staff_can_edit_own_profile_but_cannot_inject_role_or_status(self):
        self.login_as("staff")
        response = self.client.patch("/auth/me/profile", json={"full_name": "Staff Name", "email": "staff@example.com"})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["full_name"], "Staff Name")
        for changes in ({"role": "superadmin"}, {"is_active": False}):
            self.assertEqual(self.client.patch("/auth/me/profile", json=changes).status_code, 422)
            self.assertEqual(self.client.patch(f"/users/{self.staff_id}", json=changes).status_code, 403)

    def test_disabled_user_cannot_login_or_use_existing_session(self):
        with TestClient(self.app, base_url="http://localhost", headers={"Origin": self.origin}) as staff:
            self.login_as("staff", client=staff)
            self.login_as()
            self.assertEqual(self.client.delete(f"/users/{self.staff_id}").status_code, 204)
            response = self.client.get(f"/users/{self.staff_id}")
            self.assertEqual(response.status_code, 200, response.text)
            self.assertFalse(response.json()["is_active"])
            self.assertEqual(staff.get("/auth/me").status_code, 401)
            self.assertEqual(staff.post("/auth/login", json={"username": "staff", "password": self.password}).status_code, 401)

    def test_current_database_role_applies_to_existing_session(self):
        self.login_as()
        second = self.create_account().json()["id"]
        self.assertEqual(self.client.patch(f"/users/{self.admin_id}", json={"role": "staff"}).status_code, 200)
        self.assertEqual(self.client.get("/users").status_code, 403)
        self.login_as("secondadmin")
        self.assertEqual(self.client.patch(f"/users/{second}", json={"role": "staff"}).status_code, 403)
        self.assertEqual(self.client.delete(f"/users/{second}").status_code, 403)

    def test_superadmin_can_reset_another_superadmin_and_email_login_updates_last_login(self):
        self.login_as()
        second = self.create_account(email="owner.with.long.email.address@example.com").json()["id"]
        response = self.client.patch(f"/users/{second}", json={"username": "renamedowner", "password": "ChangedOwner10@"})
        self.assertEqual(response.status_code, 200, response.text)
        self.login_as("OWNER.WITH.LONG.EMAIL.ADDRESS@EXAMPLE.COM", "ChangedOwner10@")
        with Session(self.engine) as db:
            self.assertIsNotNone(db.get(User, UUID(second)).last_login)

    def test_own_password_change_verifies_current_password_and_revokes_session(self):
        self.login_as("staff")
        response = self.client.patch("/auth/me/password", json={"password": "ChangedOwn10@", "current_password": "wrong"})
        self.assertEqual(response.status_code, 403)
        response = self.client.patch("/auth/me/password", json={"password": "ChangedOwn10@", "current_password": self.password})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(self.client.get("/auth/me").status_code, 401)
        self.login_as("staff", "ChangedOwn10@")
