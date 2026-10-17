from concurrent.futures import ThreadPoolExecutor
from datetime import date
from decimal import Decimal
from threading import Barrier
from types import SimpleNamespace
from uuid import uuid4
from sqlalchemy.orm import Session
from tests.helpers.postgres import PostgresSecurityTestCase
from models import User,Material,Flower,FlowerMaterial,Product,ProductFlower,CustomBouquet,InventoryBalance
from schemas.order_schema import OrderCreate,OrderItemInput
from use_cases.orders.create_order import create_order
from use_cases.orders.snapshot_order import snapshot_order
from crud.orders_crud import items

class CustomOrderConcurrencyTests(PostgresSecurityTestCase):
    def test_mixed_custom_and_product_orders_lock_shared_recipe_consistently(self):
        with Session(self.engine) as db:
            material=Material(sku='MIX-M',name='Mixed material',base_unit='pcs')
            flower=Flower(sku='MIX-F',name='Mixed flower',selling_price=100,estimated_labor_cost=0)
            product=Product(sku='MIX-P',name='Mixed product',selling_price=200,assembly_labor_cost=0)
            db.add_all([material,flower,product]);db.flush()
            db.add_all([InventoryBalance(material_id=material.id,quantity_on_hand=100,average_unit_cost=10,has_received_cost=True),FlowerMaterial(flower_id=flower.id,material_id=material.id,quantity_required=Decimal(1),unit='pcs'),ProductFlower(product_id=product.id,flower_id=flower.id,quantity_required=Decimal(2))])
            recipe={'flowers':[{'flower_id':str(flower.id),'quantity':1}],'options':[],'materials':[{'material_id':str(material.id),'quantity':'1','unit':'pcs'}],'labor_cost':'0','estimated_hpp':'10','cost_complete':True}
            config=CustomBouquet(configuration_number='MIX-'+uuid4().hex,name='Mixed custom',status='finalized',proposed_price=100,final_price=100,recipe_snapshot=recipe,personalization={})
            db.add(config);db.commit();product_id,config_id=product.id,config.id
        barrier=Barrier(2)
        def run(reverse):
            with Session(self.engine) as db:
                actor=SimpleNamespace(user=db.get(User,self.user_id))
                refs=[OrderItemInput(product_id=product_id),OrderItemInput(custom_bouquet_id=config_id)]
                barrier.wait(timeout=10)
                order=create_order(db,actor,OrderCreate(customer_name='Concurrency dummy',items=refs[::-1] if reverse else refs))
                rows=items(db,order.id);snapshot_order(db,rows);db.commit()
                return order.total_amount
        with ThreadPoolExecutor(max_workers=2) as pool:self.assertEqual(list(pool.map(run,[False,True])),[300,300])
