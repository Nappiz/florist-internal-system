from concurrent.futures import ThreadPoolExecutor
from datetime import date
from decimal import Decimal
from threading import Barrier
from types import SimpleNamespace
from uuid import UUID, uuid4

from fastapi import HTTPException
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from models import User
from models.inventory_balance_model import InventoryBalance
from models.inventory_movement_model import InventoryMovement
from models.material_model import Material
from models.purchase_item_model import PurchaseItem
from models.purchase_model import Purchase
from models.supplier_store_model import SupplierStore
from tests.helpers.postgres import PostgresSecurityTestCase
from use_cases.purchases.receive import receive


class ReceivingConcurrencyTests(PostgresSecurityTestCase):
    def setUp(self):
        super().setUp()
        self.next_item_id = 1
        with Session(self.engine) as db:
            supplier = SupplierStore(name="Concurrency supplier", platform="offline")
            materials = [Material(sku=f"MAT-{index}", name=f"Material {index}", base_unit="pcs") for index in range(2)]
            db.add_all([supplier, *materials])
            db.flush()
            self.supplier_id = supplier.id
            self.material_ids = [material.id for material in materials]
            db.add_all([InventoryBalance(material_id=identity) for identity in self.material_ids])
            db.commit()

    def purchase(self, rows, *, shipping=0, discount=0):
        """Rows are (material index, base quantity, unit price), in item-id order."""
        identity = uuid4()
        subtotal = sum(int(Decimal(quantity) * unit_price) for _, quantity, unit_price in rows)
        with Session(self.engine) as db:
            db.add(Purchase(id=identity, purchase_number=f"TEST-{identity.hex}", supplier_id=self.supplier_id, purchase_date=date(2026, 10, 1), status="ordered", payment_status="unpaid", subtotal=subtotal, shipping_cost=shipping, discount_amount=discount, total_amount=subtotal + shipping - discount, created_by=self.user_id, updated_by=self.user_id))
            db.flush()
            for material_index, quantity, unit_price in rows:
                db.add(PurchaseItem(id=UUID(int=self.next_item_id), purchase_id=identity, material_id=self.material_ids[material_index], material_name_snapshot=f"Material {material_index}", base_unit_snapshot="pcs", quantity=Decimal(quantity), quantity_base=Decimal(quantity), unit_price=unit_price, subtotal=int(Decimal(quantity) * unit_price)))
                self.next_item_id += 1
            db.commit()
        return identity

    def simultaneous_receipts(self, identities):
        barrier = Barrier(len(identities), timeout=20)

        def worker(identity):
            with Session(self.engine) as db:
                # Fail boundedly if lock ordering regresses, rather than hanging CI.
                db.execute(text("SET LOCAL lock_timeout = '10s'"))
                db.execute(text("SET LOCAL statement_timeout = '20s'"))
                actor = SimpleNamespace(user=db.get(User, self.user_id))
                barrier.wait()
                try:
                    result = receive(db, actor, identity)
                    return 200, result["status"]
                except HTTPException as error:
                    db.rollback()
                    return error.status_code, None

        with ThreadPoolExecutor(max_workers=len(identities)) as executor:
            futures = [executor.submit(worker, identity) for identity in identities]
            return [future.result(timeout=40) for future in futures]

    def test_simultaneous_receiving_of_same_purchase_records_one_in(self):
        identity = self.purchase([(0, "10", 100)])
        results = self.simultaneous_receipts([identity, identity])
        self.assertEqual(sorted(code for code, _ in results), [200, 409])
        with Session(self.engine) as db:
            self.assertEqual(db.get(Purchase, identity).status, "received")
            movements = db.scalars(select(InventoryMovement).where(InventoryMovement.reference_id == identity)).all()
            self.assertEqual(len(movements), 1)
            self.assertEqual(movements[0].movement_type, "IN")
            self.assertEqual(movements[0].quantity_delta, Decimal("10"))
            self.assertEqual(db.get(InventoryBalance, self.material_ids[0]).quantity_on_hand, Decimal("10"))

    def test_opposite_material_item_orders_receive_without_deadlock(self):
        first = self.purchase([(0, "10", 100), (1, "20", 200)])
        second = self.purchase([(1, "3", 300), (0, "2", 200)])
        results = self.simultaneous_receipts([first, second])
        self.assertEqual(results, [(200, "received"), (200, "received")])
        with Session(self.engine) as db:
            self.assertEqual(db.get(InventoryBalance, self.material_ids[0]).quantity_on_hand, Decimal("12"))
            self.assertEqual(db.get(InventoryBalance, self.material_ids[1]).quantity_on_hand, Decimal("23"))
            self.assertEqual(db.scalar(select(func.count()).select_from(InventoryMovement)), 4)

    def test_weighted_average_excludes_shipping_and_header_discount(self):
        first = self.purchase([(0, "10", 100)], shipping=500, discount=100)
        second = self.purchase([(0, "20", 200)], shipping=700, discount=400)
        for identity in (first, second):
            with Session(self.engine) as db:
                actor = SimpleNamespace(user=db.get(User, self.user_id))
                self.assertEqual(receive(db, actor, identity)["status"], "received")
        with Session(self.engine) as db:
            balance = db.get(InventoryBalance, self.material_ids[0])
            self.assertEqual(balance.quantity_on_hand, Decimal("30"))
            self.assertEqual(balance.average_unit_cost, Decimal("166.66666667"))
            self.assertTrue(balance.has_received_cost)

    def test_database_rejects_nonfinite_inventory_values(self):
        for column in ("quantity_on_hand", "average_unit_cost"):
            for value in ("NaN", "Infinity", "-Infinity"):
                with self.subTest(column=column, value=value):
                    with Session(self.engine) as db:
                        balance = db.get(InventoryBalance, self.material_ids[0])
                        setattr(balance, column, Decimal(value))
                        with self.assertRaises(DBAPIError):
                            db.flush()
                        db.rollback()
