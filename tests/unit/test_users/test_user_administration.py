import secrets
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from starlette.requests import Request

from configs.auth_dependencies import administration_context
from models import AuthSession, User
from schemas.user_schema import UserUpdate
from services.user_security import csrf_token_for, hash_password, hash_token
from tests.helpers.postgres import PostgresSecurityTestCase
from use_cases.users.update_user import update_user


class UserAdministrationConcurrencyTests(PostgresSecurityTestCase):
    def setUp(self):
        super().setUp()
        self.tokens = [secrets.token_urlsafe(32), secrets.token_urlsafe(32)]
        self.admin_ids = []
        with Session(self.engine) as db:
            for index, token in enumerate(self.tokens):
                admin = User(username=f"admin{index}", password_hash=hash_password(self.password), is_superadmin=True)
                db.add(admin)
                db.flush()
                self.admin_ids.append(admin.id)
                db.add(AuthSession(user_id=admin.id, token_hash=hash_token(token), credential_version=0,
                    expires_at=datetime.now(UTC) + timedelta(hours=24)))
            db.commit()

    def run_concurrent_changes(self, changes, target_other=False):
        barrier = threading.Barrier(2)

        def mutate(index):
            token = self.tokens[index]
            request = Request({"type": "http", "headers": [(b"cookie", ("florist_session=" + token).encode()),
                (b"origin", b"http://localhost:3000")]})
            with Session(self.engine) as db:
                barrier.wait(timeout=10)
                try:
                    actor = administration_context(request, csrf_token_for(token), db)
                    target = self.admin_ids[1 - index if target_other else index]
                    update_user(db, actor, target, UserUpdate(**changes), "192.0.2.1")
                    return 200
                except HTTPException as error:
                    return error.status_code

        with patch("use_cases.auth.validate_origin.get_settings") as settings, patch("configs.auth_dependencies.get_settings") as dependency_settings:
            settings.return_value.allowed_origins = ["http://localhost:3000"]
            dependency_settings.return_value.session_cookie_name = "florist_session"
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(mutate, range(2)))
        self.assertEqual(sorted(results), [200, 403])
        with Session(self.engine) as db:
            remaining = db.scalar(select(func.count()).select_from(User).where(User.role == "superadmin", User.is_active.is_(True)))
            self.assertEqual(remaining, 1)

    def test_simultaneous_self_disables_leave_one_active_superadmin(self):
        self.run_concurrent_changes({"is_active": False})

    def test_two_superadmins_demoting_each_other_do_not_deadlock(self):
        self.run_concurrent_changes({"role": "staff"}, target_other=True)
