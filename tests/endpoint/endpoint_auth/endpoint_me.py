from datetime import UTC, datetime, timedelta

from sqlalchemy import update
from sqlalchemy.orm import Session

from models import AuthSession, User
from tests.helpers.auth import AuthEndpointTestCase


class MeEndpointTests(AuthEndpointTestCase):
    def test_requires_login_and_returns_only_public_user_fields(self):
        self.assertEqual(self.client.get("/auth/me").status_code, 401)
        self.login_as("staff")
        response = self.client.get("/auth/me")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"]["id"], self.staff_id)
        self.assertNotIn("password_hash", response.text)
        self.assertNotIn("token_hash", response.text)
        self.assertEqual(response.headers["cache-control"], "no-store")

    def test_expired_session_is_rejected(self):
        self.login_as("staff")
        with Session(self.engine) as db:
            db.execute(update(AuthSession).values(expires_at=datetime.now(UTC) - timedelta(seconds=1)))
            db.commit()
        self.assertEqual(self.client.get("/auth/me").status_code, 401)

    def test_old_credential_version_is_rejected_even_if_session_row_remains(self):
        self.login_as("staff")
        with Session(self.engine) as db:
            db.execute(update(User).where(User.username == "staff").values(credential_version=1))
            db.commit()
        self.assertEqual(self.client.get("/auth/me").status_code, 401)

    def test_invalid_token_is_rejected(self):
        self.client.cookies.set("florist_session", "invalid")
        self.assertEqual(self.client.get("/auth/me").status_code, 401)
