from decimal import Decimal

from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import AuthSession, Expense, Supplier, User
from schemas.auth_schema import AuthContext
from schemas.expense_schema import ExpenseCreate, ExpenseUpdate
from schemas.supplier_schema import SupplierCreate, SupplierUpdate
from tests.helpers.postgres import PostgresSecurityTestCase
from use_cases.expenses.create_expense import create_expense
from use_cases.expenses.get_expense import get_expense
from use_cases.expenses.update_expense import update_expense
from use_cases.suppliers.create_supplier import create_supplier
from use_cases.suppliers.update_supplier import update_supplier


class ExpensePersistenceTests(PostgresSecurityTestCase):
    def actor(self, db):
        return AuthContext(user=db.get(User, self.user_id), session=AuthSession(), csrf_token="test-context")

    def supplier(self, db, actor):
        return create_supplier(db, actor, SupplierCreate(
            material_name="Pipe Cleaner", store_name="Purchase Test", purchase_url="https://example.com/product",
            price="123456789012.34", pack_quantity="125.500", unit="pcs",
        ))

    def test_exact_money_snapshot_and_history_after_supplier_and_user_deletion(self):
        with Session(self.engine) as db:
            actor = self.actor(db)
            supplier = self.supplier(db, actor)
            record = create_expense(db, actor, ExpenseCreate(supplier_id=supplier.id, pack_count=3, shipping_cost="0.20", discount_amount="0.05"))
            self.assertEqual(record.total_amount, Decimal("370370367037.17"))
            self.assertEqual(record.total_quantity, Decimal("376.500"))
            update_supplier(db, actor, supplier.id, SupplierUpdate(price="1", pack_quantity="1", material_name="Changed"))
            updated = update_expense(db, actor, record.id, ExpenseUpdate(supplier_id=supplier.id, pack_count=4))
            self.assertEqual(updated.total_amount, Decimal("493827156049.51"))
            self.assertEqual(updated.material_name,"Pipe Cleaner")
            db.delete(db.get(Supplier, supplier.id))
            db.commit()
            history = get_expense(db,record.id)
            self.assertIsNone(history.supplier_id)
            self.assertEqual(history.price_per_pack,Decimal("123456789012.34"))
            update_expense(db, actor, record.id, ExpenseUpdate(notes="Stored after deletion"))
            db.delete(db.get(User,self.user_id))
            db.commit()
            history = get_expense(db,record.id)
            self.assertIsNone(history.created_by)
            self.assertIsNone(history.updated_by)
            self.assertEqual(history.total_amount,Decimal("493827156049.51"))

    def test_constraints_reject_nonfinite_and_inconsistent_totals_at_database_boundary(self):
        with Session(self.engine) as db:
            actor = self.actor(db)
            record = create_expense(db,actor,ExpenseCreate(supplier_id=self.supplier(db,actor).id,pack_count=3,price_per_pack="0.10"))
            self.assertEqual(record.total_amount,Decimal("0.30"))
            cases = [{field:Decimal("NaN")} for field in (
                "price_per_pack","shipping_cost","discount_amount","subtotal_amount","total_amount","pack_quantity",
            )] + [{"subtotal_amount":Decimal("0.99")},{"total_amount":Decimal("0.99")},{"pack_count":0}]
            for values in cases:
                with self.subTest(values=values), self.assertRaises(IntegrityError):
                    with db.begin_nested():
                        db.execute(update(Expense).where(Expense.id==record.id).values(**values))
            self.assertEqual(get_expense(db,record.id).total_amount,Decimal("0.30"))
