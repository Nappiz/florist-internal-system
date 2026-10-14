from sqlalchemy import select
from sqlalchemy.orm import Session

from models import User
from services.user_security import verify_password
from tests.helpers.auth import AuthEndpointTestCase


class CreateUserEndpointTests(AuthEndpointTestCase):
    def test_only_superadmin_can_create_and_password_is_hashed(self):
        self.assertEqual(self.client.post("/users", json={"username": "newstaff", "password": self.password}).status_code, 401)
        self.login_as("staff")
        self.assertEqual(self.client.post("/users", json={"username": "newstaff", "password": self.password}).status_code, 403)
        self.login_as()
        response = self.client.post("/users", json={"username": "NEWSTAFF", "password": self.password})
        self.assertEqual(response.status_code, 201, response.text)
        self.assertFalse(response.json()["is_superadmin"])
        self.assertEqual(response.json()["username"], "newstaff")
        self.assertNotIn(self.password, response.text)
        with Session(self.engine) as db:
            user = db.scalar(select(User).where(User.username == "newstaff"))
            self.assertNotEqual(user.password_hash, self.password)
            self.assertTrue(verify_password(user.password_hash, self.password))

    def test_rejects_weak_passwords_role_injection_and_duplicate_username(self):
        self.login_as()
        for password in ("Short@1", "nouppercase@", "NOLOWERCASE@", "NoSpecial10"):
            with self.subTest(password=password):
                response = self.client.post("/users", json={"username": "newstaff", "password": password})
                self.assertEqual(response.status_code, 422)
                self.assertNotIn(password, response.text)
        response = self.client.post("/users", json={"username": "newstaff", "password": self.password, "is_superadmin": True})
        self.assertEqual(response.status_code, 422)
        self.assertNotIn(self.password, response.text)
        self.assertEqual(self.client.post("/users", json={"username": "STAFF", "password": self.password}).status_code, 409)

    def test_mutation_requires_session_bound_csrf(self):
        self.login_as()
        self.client.headers["X-CSRF-Token"] = "a" * 64
        self.assertEqual(self.client.post("/users", json={"username": "newstaff", "password": self.password}).status_code, 403)
