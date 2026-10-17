import csv
from datetime import date
from io import StringIO
from types import SimpleNamespace
from sqlalchemy.orm import Session
from models import User
from schemas.cashflow_schema import CashflowQuery
from tests.helpers.postgres import PostgresSecurityTestCase
from use_cases.cashflow.common import movement
from use_cases.cashflow.export import export


class ExportSnapshotTests(PostgresSecurityTestCase):
    def test_single_cursor_snapshot_survives_backdated_commit_on_another_connection(self):
        with Session(self.engine) as reader:
            user = reader.get(User, self.user_id)
            user.role, user.is_superadmin = 'superadmin', True
            actor = SimpleNamespace(user=user)
            original = set()
            for _ in range(600):
                row = movement(reader, actor, account_id=self.cash_account_id, transaction_date=date(2026, 1, 2), direction='IN', amount=1, category='correction', source_type='adjustment')
                original.add(row.transaction_number)
            reader.commit()
            chunks = export(reader, actor, CashflowQuery())
            header, first = next(chunks), next(chunks)
            with Session(self.engine) as writer:
                movement(writer, actor, account_id=self.cash_account_id, transaction_date=date(2026, 1, 1), direction='IN', amount=1, category='correction', source_type='adjustment')
                writer.commit()
            rows = list(csv.reader(StringIO(header.lstrip('\ufeff') + first + ''.join(chunks))))[1:]
            references = [row[4] for row in rows]
            self.assertEqual(len(references), 600)
            self.assertEqual(set(references), original)
