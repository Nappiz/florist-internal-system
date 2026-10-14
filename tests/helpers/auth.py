import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from configs.database import get_db
from configs.settings import get_settings
from main import create_app
from models import Base, User
from services.user_security import hash_password


class AuthEndpointTestCase(unittest.TestCase):
    origin = "http://localhost:3000"
    password = "Example10@"

    def setUp(self):
        self.environment = patch.dict(os.environ, {
            "APP_ENV": "development",
            "ALLOWED_ORIGINS": '["http://localhost:3000"]',
            "ALLOWED_HOSTS": '["localhost"]',
        })
        self.environment.start()
        get_settings.cache_clear()
        self.engine = create_engine(
            "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
        )
        event.listen(self.engine, "connect", lambda connection, _: connection.execute("PRAGMA foreign_keys=ON"))
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            admin = User(username="superadmin", password_hash=hash_password(self.password), is_superadmin=True)
            ordinary = User(username="staff", password_hash=hash_password(self.password), is_superadmin=False)
            db.add_all([admin, ordinary])
            db.commit()
            self.admin_id = str(admin.id)
            self.staff_id = str(ordinary.id)

        self.app = create_app()

        def test_db():
            with Session(self.engine) as db:
                yield db

        self.app.dependency_overrides[get_db] = test_db
        self.client = TestClient(self.app, base_url="http://localhost", headers={"Origin": self.origin})

    def tearDown(self):
        self.client.close()
        self.engine.dispose()
        self.environment.stop()
        get_settings.cache_clear()

    def login_as(self, username="superadmin", password=None, client=None):
        client = client or self.client
        response = client.post("/auth/login", json={"username": username, "password": password or self.password})
        self.assertEqual(response.status_code, 200, response.text)
        client.headers["X-CSRF-Token"] = response.json()["csrf_token"]
        return response
