from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models import Supplier, User
from tests.helpers.postgres import PostgresSecurityTestCase


class SupplierPersistenceTests(PostgresSecurityTestCase):
    def test_database_rejects_nonfinite_money_and_quantity(self):
        for field in ("price", "pack_quantity", "estimated_shipping_cost"):
            with self.subTest(field=field):
                values = dict(
                    material_name="Invalid Numeric", store_name="Constraint Test",
                    purchase_url="https://example.com/product", price=Decimal("100.00"),
                    pack_quantity=Decimal("1.000"), unit="pcs", last_checked_at=datetime.now(UTC).date(),
                )
                values[field] = Decimal("NaN")
                with Session(self.engine) as db:
                    db.add(Supplier(**values))
                    with self.assertRaises(IntegrityError):
                        db.flush()

    def test_exact_decimal_values_and_research_survive_author_deletion(self):
        with Session(self.engine) as db:
            record = Supplier(
                material_name="Pipe Cleaner", store_name="Persistence Test",
                purchase_url="https://example.com/product", price=Decimal("12345.67"),
                pack_quantity=Decimal("125.500"), unit="pcs",
                estimated_shipping_cost=Decimal("3456.78"),
                last_checked_at=datetime.now(UTC).date(), created_by=self.user_id, updated_by=self.user_id,
            )
            db.add(record)
            db.commit()
            record_id = record.id
            db.delete(db.get(User, self.user_id))
            db.commit()
        with Session(self.engine) as db:
            record = db.get(Supplier, record_id)
            self.assertIsNotNone(record)
            self.assertEqual(record.price, Decimal("12345.67"))
            self.assertEqual(record.pack_quantity, Decimal("125.500"))
            self.assertEqual(record.estimated_shipping_cost, Decimal("3456.78"))
            self.assertIsNone(record.created_by)
            self.assertIsNone(record.updated_by)
