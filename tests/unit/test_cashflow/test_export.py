import csv
from datetime import timedelta
from io import StringIO
from uuid import uuid4
from tests.unit.test_cashflow.base import CashTestCase
from use_cases.cashflow.common import movement
from use_cases.cashflow.export import export
from schemas.cashflow_schema import CashflowQuery


class ExportTests(CashTestCase):
    def test_backdated_insert_between_chunks_never_duplicates_or_omits_original_rows(self):
        account = self.account(amount=0)
        original = set()
        for _ in range(600):
            row = movement(self.db, self.actor, account_id=account['id'], transaction_date=self.day + timedelta(days=1), direction='IN', amount=1, category='correction', source_type='adjustment', source_id=uuid4())
            original.add(row.transaction_number)
        self.db.commit()
        chunks = export(self.db, self.actor, CashflowQuery())
        header, first = next(chunks), next(chunks)
        movement(self.db, self.actor, account_id=account['id'], transaction_date=self.day, direction='IN', amount=1, category='correction', source_type='adjustment', source_id=uuid4())
        self.db.commit()
        rows = list(csv.reader(StringIO(header.lstrip('\ufeff') + first + ''.join(chunks))))[1:]
        references = [row[4] for row in rows]
        self.assertEqual(len(references), 600)
        self.assertEqual(set(references), original)
