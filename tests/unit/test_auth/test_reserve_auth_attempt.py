from concurrent.futures import ThreadPoolExecutor

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import LoginThrottle
from services.user_security import hash_token
from tests.helpers.postgres import PostgresSecurityTestCase
from use_cases.auth.reserve_auth_attempt import reserve_auth_attempt


class AuthAttemptConcurrencyTests(PostgresSecurityTestCase):
    def test_parallel_workers_share_one_atomic_account_limit(self):
        def attempt(index):
            with Session(self.engine) as db:
                try:
                    reserve_auth_attempt(db, "staff", f"192.0.2.{index}")
                    db.commit()
                    return 200
                except HTTPException as error:
                    return error.status_code

        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(attempt, range(6)))
        self.assertEqual(results.count(200), 5)
        self.assertEqual(results.count(429), 1)
        with Session(self.engine) as db:
            bucket = db.scalar(select(LoginThrottle).where(LoginThrottle.bucket_key == hash_token("username:staff")))
            self.assertEqual(bucket.attempts, 6)
