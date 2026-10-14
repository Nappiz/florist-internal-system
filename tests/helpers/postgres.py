import os
import re
import unittest
from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateSchema, DropSchema

from configs.database import get_engine
from models import Base, User
from services.user_security import hash_password


@unittest.skipUnless(os.getenv("RUN_POSTGRES_SECURITY_TESTS") == "1", "Opt-in PostgreSQL tests use a temporary schema.")
class PostgresSecurityTestCase(unittest.TestCase):
    password = "OriginalTest10@"

    def setUp(self):
        self.schema_name = "auth_verify_" + uuid4().hex[:12]
        self.base_engine = get_engine()
        with self.base_engine.begin() as connection:
            connection.execute(CreateSchema(self.schema_name))
        self.addCleanup(self.cleanup_schema)
        self.engine = self.base_engine.execution_options(schema_translate_map={None: self.schema_name})
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            user = User(username="staff", password_hash=hash_password(self.password), is_superadmin=False)
            db.add(user)
            db.commit()
            self.user_id = user.id

    def cleanup_schema(self):
        if re.fullmatch(r"auth_verify_[a-f0-9]{12}", self.schema_name) is None:
            raise RuntimeError("Refusing to drop an unexpected schema")
        with self.base_engine.begin() as connection:
            connection.execute(DropSchema(self.schema_name, cascade=True))
        self.base_engine.dispose()
