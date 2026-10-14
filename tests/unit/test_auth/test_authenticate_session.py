import secrets
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import event
from sqlalchemy.orm import Session

from crud import auth_sessions_crud, users_crud
from models import AuthSession
from services.user_security import hash_token
from tests.helpers.postgres import PostgresSecurityTestCase
from use_cases.auth.authenticate_session import authenticate_session


class AuthenticateSessionConcurrencyTests(PostgresSecurityTestCase):
    def waiting_authentication(self, token, waiting):
        def reached_lock(connection, cursor, statement, parameters, context, executemany):
            if threading.current_thread().name.startswith("security-waiter") and "FOR UPDATE" in statement:
                waiting.set()

        event.listen(self.engine, "before_cursor_execute", reached_lock)
        self.addCleanup(lambda: event.remove(self.engine, "before_cursor_execute", reached_lock))

        def authenticate():
            with Session(self.engine) as db:
                try:
                    authenticate_session(db, token)
                    return 200
                except HTTPException as error:
                    return error.status_code

        return authenticate

    def test_session_expiring_while_waiting_for_user_lock_is_rejected(self):
        token = secrets.token_urlsafe(32)
        expires = datetime.now(UTC) + timedelta(seconds=2)
        with Session(self.engine) as db:
            db.add(AuthSession(user_id=self.user_id, token_hash=hash_token(token), credential_version=0, expires_at=expires))
            db.commit()
        waiting = threading.Event()
        authenticate = self.waiting_authentication(token, waiting)
        with ThreadPoolExecutor(max_workers=1, thread_name_prefix="security-waiter") as pool:
            with Session(self.engine) as locked:
                users_crud.get_by_id(locked, self.user_id)
                future = pool.submit(authenticate)
                self.assertTrue(waiting.wait(10), "Authentication never reached the user lock")
                time.sleep(max(0, (expires - datetime.now(UTC)).total_seconds()) + 0.1)
                locked.commit()
            self.assertEqual(future.result(timeout=10), 401)

    def test_logout_committed_during_authentication_does_not_restore_deleted_session(self):
        token = secrets.token_urlsafe(32)
        with Session(self.engine) as db:
            session = AuthSession(user_id=self.user_id, token_hash=hash_token(token), credential_version=0, expires_at=datetime.now(UTC) + timedelta(hours=24))
            db.add(session)
            db.commit()
            session_id = session.id
        waiting = threading.Event()
        authenticate = self.waiting_authentication(token, waiting)
        with ThreadPoolExecutor(max_workers=1, thread_name_prefix="security-waiter") as pool:
            with Session(self.engine) as locked:
                users_crud.get_by_id(locked, self.user_id)
                future = pool.submit(authenticate)
                self.assertTrue(waiting.wait(10), "Authentication never reached the user lock")
                auth_sessions_crud.revoke_session(locked, session_id)
                locked.commit()
            self.assertEqual(future.result(timeout=10), 401)
