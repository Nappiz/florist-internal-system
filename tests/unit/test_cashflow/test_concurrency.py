from concurrent.futures import ThreadPoolExecutor
from datetime import date
from threading import Barrier
from types import SimpleNamespace
from uuid import uuid4
from sqlalchemy import select,func
from sqlalchemy.orm import Session
from fastapi import HTTPException
from tests.helpers.postgres import PostgresSecurityTestCase
from models import User,CashAccount,CashTransaction,CashOperation,Order,OrderPayment
from schemas.cashflow_schema import AdjustmentInput,TransferInput
from schemas.order_schema import OrderPaymentCreate
from use_cases.cashflow.adjust import adjust
from use_cases.cashflow.transfer import transfer
from use_cases.orders.add_payment import add_payment

class CashConcurrencyTests(PostgresSecurityTestCase):
    def setUp(self):
        super().setUp()
        with Session(self.engine) as db:
            user=db.get(User,self.user_id);user.is_superadmin=True;user.role='superadmin';db.commit()
        self.day=date(2026,10,1)

    def parallel(self,operations):
        barrier=Barrier(len(operations))
        def run(operation):
            with Session(self.engine) as db:
                actor=SimpleNamespace(user=db.get(User,self.user_id))
                barrier.wait(timeout=10)
                try:operation(db,actor);return 200
                except HTTPException as e:db.rollback();return e.status_code
        with ThreadPoolExecutor(max_workers=len(operations)) as pool:return list(pool.map(run,operations))

    def test_same_adjustment_key_concurrently_posts_once(self):
        data=AdjustmentInput(operation_key=uuid4(),cash_account_id=self.cash_account_id,transaction_date=self.day,direction='IN',amount=100,category='capital_contribution',reason='Concurrency proof')
        self.assertEqual(self.parallel([lambda db,actor:adjust(db,actor,data)]*2),[200,200])
        with Session(self.engine) as db:
            self.assertEqual(db.scalar(select(func.count()).select_from(CashTransaction)),1)
            self.assertEqual(db.scalar(select(func.count()).select_from(CashOperation)),1)

    def test_opposite_transfers_lock_accounts_without_deadlock(self):
        with Session(self.engine) as db:
            account=CashAccount(name='Second test account',account_type='bank',opening_date=date(2020,1,1),history_mode='backfill')
            db.add(account);db.commit();second=account.id
        a=TransferInput(operation_key=uuid4(),from_account_id=self.cash_account_id,to_account_id=second,transaction_date=self.day,amount=10,reason='A to B')
        b=TransferInput(operation_key=uuid4(),from_account_id=second,to_account_id=self.cash_account_id,transaction_date=self.day,amount=20,reason='B to A')
        self.assertEqual(self.parallel([lambda db,actor:transfer(db,actor,a),lambda db,actor:transfer(db,actor,b)]),[200,200])
        from crud.cashflow_crud import balance
        with Session(self.engine) as db:
            self.assertEqual(balance(db,self.cash_account_id),10)
            self.assertEqual(balance(db,second),-10)
            self.assertEqual(db.scalar(select(func.count()).select_from(CashTransaction)),4)

    def test_distinct_order_payments_share_account_without_lost_cash(self):
        with Session(self.engine) as db:
            rows=[Order(order_number='CASH-'+uuid4().hex,customer_name='Concurrency dummy',order_date=self.day,subtotal=100,total_amount=100) for _ in range(2)]
            db.add_all(rows);db.commit();ids=[row.id for row in rows]
        operations=[]
        for identity in ids:
            data=OrderPaymentCreate(payment_key=uuid4(),cash_account_id=self.cash_account_id,payment_date=self.day,amount=50)
            operations.append(lambda db,actor,identity=identity,data=data:add_payment(db,actor,identity,data))
        self.assertEqual(self.parallel(operations),[200,200])
        with Session(self.engine) as db:
            self.assertEqual(db.scalar(select(func.count()).select_from(OrderPayment)),2)
            self.assertEqual(db.scalar(select(func.sum(CashTransaction.amount))),100)
