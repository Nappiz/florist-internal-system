import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from models import Base, User
from services.user_security import hash_password, verify_password
from use_cases.users.seed_superadmin import seed_superadmin


class SeedSuperadminTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_seed_is_idempotent_and_never_resets_existing_password_or_username(self):
        first = seed_superadmin(self.db, "InitialSeed10@")
        first_hash = first.password_hash
        first_id = first.id
        first.username = "owner"
        self.db.commit()
        second = seed_superadmin(self.db, "DifferentSeed10@")
        self.assertEqual(second.id, first_id)
        self.assertEqual(second.username, "owner")
        self.assertEqual(second.password_hash, first_hash)
        self.assertTrue(verify_password(second.password_hash, "InitialSeed10@"))
        self.assertEqual(self.db.scalar(select(func.count()).select_from(User)), 1)

    def test_seed_does_not_promote_an_existing_unprivileged_account(self):
        ordinary = User(username="superadmin", password_hash=hash_password("StaffPassword10@"), is_superadmin=False)
        self.db.add(ordinary)
        self.db.commit()
        with self.assertRaises(HTTPException) as error:
            seed_superadmin(self.db, "InitialSeed10@")
        self.assertEqual(error.exception.status_code, 409)
        self.assertFalse(ordinary.is_superadmin)
