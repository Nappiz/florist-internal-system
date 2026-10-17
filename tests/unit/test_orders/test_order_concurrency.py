from concurrent.futures import ThreadPoolExecutor
from datetime import date
from decimal import Decimal
from threading import Barrier
from types import SimpleNamespace
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models.flower_model import Flower
from models.inventory_balance_model import InventoryBalance
from models.inventory_movement_model import InventoryMovement
from models.material_model import Material
from models.order_model import Order
from models.order_item_model import OrderItem
from models.order_payment_model import OrderPayment
from models.production_record_model import ProductionRecord
from models.user_model import User
from schemas.order_schema import OrderPaymentCreate
from tests.helpers.postgres import PostgresSecurityTestCase
from use_cases.orders.add_payment import add_payment
from use_cases.orders.complete_production import complete_production


class OrderConcurrencyTests(PostgresSecurityTestCase):
    def setUp(self):
        super().setUp()
        with Session(self.engine) as db:
            material = Material(sku="CONCURRENT-M", name="Production material", base_unit="pcs")
            flower = Flower(sku="CONCURRENT-F", name="Production flower", selling_price=100)
            db.add_all([material, flower])
            db.flush()
            self.material_id, self.flower_id = material.id, flower.id
            db.add(InventoryBalance(material_id=material.id, quantity_on_hand=10, average_unit_cost=100, has_received_cost=True))
            db.commit()

    def make_order(self, status="in_production"):
        with Session(self.engine) as db:
            order = Order(order_number="CONCURRENT-" + uuid4().hex, customer_name="Customer", order_date=date(2026, 10, 15), subtotal=100, total_amount=100, status=status)
            db.add(order)
            db.flush()
            db.add(OrderItem(order_id=order.id, flower_id=self.flower_id, item_name_snapshot="Frozen flower", quantity=1, unit_price=100, subtotal=100, labor_cost_snapshot=500, recipe_snapshot={"materials":[{"material_id":str(self.material_id),"quantity":"2.000000","unit":"pcs"}]}))
            db.commit()
            return order.id

    def concurrently(self, operations):
        barrier = Barrier(len(operations))

        def run(operation):
            with Session(self.engine) as db:
                actor = SimpleNamespace(user=db.get(User, self.user_id))
                barrier.wait(timeout=10)
                try:
                    operation(db, actor)
                    return 200
                except HTTPException as error:
                    return error.status_code

        with ThreadPoolExecutor(max_workers=len(operations)) as pool:
            return list(pool.map(run, operations))

    def test_parallel_production_of_same_order_creates_one_record_and_outflow(self):
        identity = self.make_order()
        result = self.concurrently([lambda db, actor: complete_production(db, actor, identity)] * 2)
        self.assertEqual(sorted(result), [200, 409])
        with Session(self.engine) as db:
            self.assertEqual(db.get(InventoryBalance, self.material_id).quantity_on_hand, Decimal("8"))
            self.assertEqual(db.scalar(select(func.count()).select_from(ProductionRecord)), 1)
            self.assertEqual(db.scalar(select(func.count()).select_from(InventoryMovement)), 1)

    def test_parallel_orders_cannot_overdraw_shared_material(self):
        identities = [self.make_order(), self.make_order()]
        with Session(self.engine) as db:
            for item in db.scalars(select(OrderItem).where(OrderItem.order_id.in_(identities))):
                item.recipe_snapshot = {"materials":[{"material_id":str(self.material_id),"quantity":"8.000000","unit":"pcs"}]}
            db.commit()
        result = self.concurrently([lambda db, actor, identity=identity: complete_production(db, actor, identity) for identity in identities])
        self.assertEqual(sorted(result), [200, 409])
        with Session(self.engine) as db:
            self.assertEqual(db.get(InventoryBalance, self.material_id).quantity_on_hand, Decimal("2"))
            self.assertEqual(db.scalar(select(func.count()).select_from(ProductionRecord)), 1)

    def test_parallel_payments_cannot_overpay_order(self):
        identity = self.make_order("confirmed")
        payments = [OrderPaymentCreate(cash_account_id=self.cash_account_id,payment_key=uuid4(), amount=60), OrderPaymentCreate(cash_account_id=self.cash_account_id,payment_key=uuid4(), amount=60)]
        result = self.concurrently([lambda db, actor, data=data: add_payment(db, actor, identity, data) for data in payments])
        self.assertEqual(sorted(result), [200, 409])
        with Session(self.engine) as db:
            self.assertEqual(db.scalar(select(func.sum(OrderPayment.amount))), 60)

    def test_parallel_retries_share_exactly_one_payment(self):
        identity = self.make_order("confirmed")
        data = OrderPaymentCreate(cash_account_id=self.cash_account_id,payment_key=uuid4(), amount=60)
        result = self.concurrently([lambda db, actor: add_payment(db, actor, identity, data)] * 2)
        self.assertEqual(result, [200, 200])
        with Session(self.engine) as db:
            self.assertEqual(db.scalar(select(func.count()).select_from(OrderPayment)), 1)
