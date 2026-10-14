import os
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import update
from sqlalchemy.orm import Session

from configs.database import get_db
from configs.settings import get_settings
from main import create_app
from models import LoginThrottle
from tests.helpers.auth import AuthEndpointTestCase


class SecurityEndpointTests(AuthEndpointTestCase):
    def test_ip_limit_cannot_be_bypassed_by_varying_username_or_forwarded_header(self):
        for index in range(30):
            response = self.client.post(
                "/auth/login", headers={"X-Forwarded-For": f"192.0.2.{index}"},
                json={"username": f"unknown{index}", "password": self.password},
            )
            self.assertEqual(response.status_code, 401)
        blocked = self.client.post("/auth/login", json={"username": "another", "password": self.password})
        self.assertEqual(blocked.status_code, 429)

    def test_expired_login_rate_window_allows_new_attempts(self):
        for _ in range(5):
            self.client.post("/auth/login", json={"username": "staff", "password": "Wrong10@"})
        with Session(self.engine) as db:
            db.execute(update(LoginThrottle).values(window_started=datetime.now(UTC) - timedelta(minutes=16)))
            db.commit()
        self.login_as("staff")

    def test_csrf_token_from_another_session_cannot_authorize_mutation(self):
        old_csrf = self.login_as().json()["csrf_token"]
        self.login_as()
        self.client.headers["X-CSRF-Token"] = old_csrf
        self.assertEqual(self.client.post("/users", json={"username": "newstaff", "password": self.password}).status_code, 403)

    def test_production_cookie_is_secure_host_only_and_http_redirects_to_https(self):
        os.environ["APP_ENV"] = "production"
        os.environ["ALLOWED_ORIGINS"] = '["https://frontend.example"]'
        get_settings.cache_clear()
        app = create_app()
        app.dependency_overrides[get_db] = self.app.dependency_overrides[get_db]
        with TestClient(app, base_url="https://localhost", headers={"Origin": "https://frontend.example"}) as client:
            response = client.post("/auth/login", json={"username": "superadmin", "password": self.password})
            self.assertEqual(response.status_code, 200, response.text)
            cookie = response.headers["set-cookie"].lower()
            self.assertIn("__host-florist_session", cookie)
            self.assertIn("secure", cookie)
            self.assertIn("httponly", cookie)
            self.assertNotIn("domain=", cookie)
            self.assertIn("strict-transport-security", response.headers)
            self.assertEqual(client.get("http://localhost/health", follow_redirects=False).status_code, 307)

    def test_host_header_is_restricted(self):
        self.assertEqual(self.client.get("/health", headers={"Host": "evil.example"}).status_code, 400)
