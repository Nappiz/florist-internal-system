from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import AuthSession
from services.user_security import hash_token
from tests.helpers.auth import AuthEndpointTestCase


class LoginEndpointTests(AuthEndpointTestCase):
    def test_login_sets_httponly_cookie_and_stores_only_token_digest_for_24_hours(self):
        response = self.login_as("SUPERADMIN")
        cookie = response.headers["set-cookie"].lower()
        self.assertIn("httponly", cookie)
        self.assertIn("samesite=strict", cookie)
        self.assertIn("max-age=86400", cookie)
        token = self.client.cookies.get("florist_session")
        self.assertNotIn(token, response.text)
        self.assertNotIn("password_hash", response.text)
        with Session(self.engine) as db:
            session = db.scalar(select(AuthSession))
            self.assertEqual(session.token_hash, hash_token(token))
            self.assertNotEqual(session.token_hash, token)
        hours = (datetime.fromisoformat(response.json()["expires_at"]) - datetime.now(UTC)).total_seconds() / 3600
        self.assertAlmostEqual(hours, 24, delta=0.01)

    def test_unknown_user_and_wrong_password_have_identical_errors(self):
        unknown = self.client.post("/auth/login", json={"username": "unknown", "password": self.password})
        wrong = self.client.post("/auth/login", json={"username": "staff", "password": "Incorrect10@"})
        self.assertEqual(unknown.status_code, 401)
        self.assertEqual(unknown.json(), wrong.json())

    def test_account_limit_blocks_even_a_correct_password_after_five_attempts(self):
        for _ in range(5):
            response = self.client.post("/auth/login", json={"username": "staff", "password": "Incorrect10@"})
            self.assertEqual(response.status_code, 401)
        blocked = self.client.post("/auth/login", json={"username": "staff", "password": self.password})
        self.assertEqual(blocked.status_code, 429)
        self.assertIn("retry-after", blocked.headers)

    def test_username_and_email_aliases_share_the_account_attempt_limit(self):
        for name in ("staff", "staff", "staff", "staff@legacy.invalid", "STAFF@LEGACY.INVALID"):
            response = self.client.post("/auth/login", json={"username": name, "password": "Incorrect10@"})
            self.assertEqual(response.status_code, 401)
        self.assertEqual(self.client.post("/auth/login", json={"username": "staff", "password": self.password}).status_code, 429)

    def test_login_requires_trusted_origin(self):
        self.assertEqual(self.client.post("/auth/login", headers={"Origin": "https://evil.example"}, json={"username": "staff", "password": self.password}).status_code, 403)
        self.client.headers.pop("Origin")
        self.assertEqual(self.client.post("/auth/login", json={"username": "staff", "password": self.password}).status_code, 403)

    def test_no_registration_endpoint(self):
        self.assertEqual(self.client.post("/auth/register", json={"username": "staff", "password": self.password}).status_code, 404)

    def test_oversize_login_body_is_rejected_without_echoing_password(self):
        response = self.client.post("/auth/login", json={"username": "staff", "password": "secret" * 4000})
        self.assertEqual(response.status_code, 413)
        self.assertNotIn("secret", response.text)
