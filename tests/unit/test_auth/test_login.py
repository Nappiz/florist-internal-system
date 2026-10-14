import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy import event
from sqlalchemy.orm import Session

from crud import auth_sessions_crud, login_throttles_crud, users_crud
from models import LoginThrottle, User
from schemas.auth_schema import LoginRequest
from services.user_security import hash_password, hash_token
from tests.helpers.postgres import PostgresSecurityTestCase
from use_cases.auth.login import login


class LoginConcurrencyTests(PostgresSecurityTestCase):
    def test_login_waiting_for_password_update_cannot_use_old_password(self):
        waiting = threading.Event()

        def reached_lock(connection, cursor, statement, parameters, context, executemany):
            if threading.current_thread().name.startswith("security-waiter") and "FOR UPDATE" in statement:
                waiting.set()

        event.listen(self.engine, "before_cursor_execute", reached_lock)
        self.addCleanup(lambda: event.remove(self.engine, "before_cursor_execute", reached_lock))

        def old_login():
            with Session(self.engine) as db:
                try:
                    login(db, LoginRequest(username="staff", password=self.password), "192.0.2.1")
                    return 200
                except HTTPException as error:
                    return error.status_code

        with ThreadPoolExecutor(max_workers=1, thread_name_prefix="security-waiter") as pool:
            with Session(self.engine) as locked:
                user = users_crud.get_by_id(locked, self.user_id)
                user.password_hash = hash_password("UpdatedTest10@")
                user.credential_version += 1
                auth_sessions_crud.revoke_user_sessions(locked, user.id)
                future = pool.submit(old_login)
                self.assertTrue(waiting.wait(10), "Login never reached the locked user")
                locked.commit()
            self.assertEqual(future.result(timeout=10), 401)

    def test_parallel_logins_refreshing_expired_counters_do_not_deadlock(self):
        names = ("alpha", "bravo")
        ips = ("192.0.2.1", "192.0.2.2")
        old = datetime.now(UTC) - timedelta(minutes=16)
        with Session(self.engine) as db:
            for name, ip in zip(names, ips):
                db.add(User(username=name, password_hash=hash_password(self.password), is_superadmin=False))
                for key in ("username:" + name, "ip:" + ip):
                    db.add(LoginThrottle(bucket_key=hash_token(key), attempts=5, window_started=old))
            db.commit()

        barrier = threading.Barrier(2)
        actual_cleanup = login_throttles_crud.delete_expired

        def synchronized_cleanup(db, cutoff):
            barrier.wait(timeout=10)
            return actual_cleanup(db, cutoff)

        def do_login(index):
            with Session(self.engine) as db:
                return login(db, LoginRequest(username=names[index], password=self.password), ips[index]).user.username

        with patch("crud.login_throttles_crud.delete_expired", synchronized_cleanup):
            with ThreadPoolExecutor(max_workers=2) as pool:
                self.assertEqual(sorted(pool.map(do_login, range(2))), ["alpha", "bravo"])
