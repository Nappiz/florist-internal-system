import unittest

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import Base, User


class UserPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        Base.metadata.create_all(self.engine)
        self.addCleanup(self.engine.dispose)

    def test_database_rejects_duplicate_email_regardless_of_case(self):
        with Session(self.engine) as db:
            db.add(User(username="alice", email="OWNER@example.com", password_hash="unused"))
            db.commit()
            db.add(User(username="bravo", email="owner@example.com", password_hash="unused"))
            with self.assertRaises(IntegrityError):
                db.commit()

    def test_multiple_superadmins_are_allowed_and_legacy_flag_must_match_role(self):
        with Session(self.engine) as db:
            db.add_all([User(username="alice", password_hash="unused", is_superadmin=True),
                User(username="bravo", password_hash="unused", is_superadmin=True)])
            db.commit()
            db.add(User(username="charlie", password_hash="unused", role="staff", is_superadmin=True))
            with self.assertRaises(IntegrityError):
                db.commit()
