from decimal import Decimal
from uuid import UUID
from types import SimpleNamespace
from sqlalchemy import select
from sqlalchemy.orm import Session
from tests.endpoint.endpoint_orders.support import OrderEndpointCase


class OrderLifecycleTests(OrderEndpointCase):
    def test_confirmation_freezes_recipe_prices_and_labor_and_production_runs_once(self):
        order=self.create_order(items=[{"flower_id":self.flower_id,"quantity":2,"unit_price":10000}])
        self.action(order["id"],"complete-production",409)
        confirmed=self.action(order["id"],"confirm").json()
        self.assertEqual(confirmed["total_amount"],20000)
        self.assertEqual(confirmed["items"][0]["recipe_snapshot"]["materials"][0]["quantity"],"2.000000")
        self.assertEqual(self.client.patch(f"/order-test/orders/{order['id']}",json={"customer_name":"Changed"}).status_code,409)
        self.action(order["id"],"confirm",409)
        self.action(order["id"],"start-production")
        self.action(order["id"],"complete-production",409)
        changed = self.client.put(f"/api/v1/flowers/{self.flower_id}/bom",json={"materials":[{"material_id":self.material_id,"quantity_required":"5","unit":"pcs"}]})
        self.assertEqual(changed.status_code,200,changed.text)
        from models.user_model import User
        from use_cases.inventory.move_stock import move_stock
        with Session(self.engine) as db:
            actor=db.get(User,UUID(self.staff_id))
            move_stock(db,SimpleNamespace(user=actor),[{"material_id":UUID(self.material_id),"quantity_delta":Decimal("10"),"unit_cost":Decimal("100")}],"adjustment",UUID(order["id"]))
            from models.flower_model import Flower
            flower=db.get(Flower,UUID(self.flower_id));flower.estimated_labor_cost=9999;flower.selling_price=99999;flower.is_active=False
            db.commit()
        ready=self.action(order["id"],"complete-production").json()
        self.assertEqual(ready["status"],"ready")
        self.assertEqual(Decimal(ready["production"]["actual_material_cost"]),Decimal("400"))
        self.assertEqual(Decimal(ready["production"]["labor_cost_snapshot"]),Decimal("1000"))
        self.action(order["id"],"complete-production",409)
        self.action(order["id"],"cancel",409)
        completed=self.action(order["id"],"complete").json()
        self.assertEqual(completed['status'],'completed')
        self.assertIn('complete_production',[entry['action'] for entry in completed['history']])
        self.assertIn('complete',[entry['action'] for entry in completed['history']])
        self.assertTrue(all('details' not in entry for entry in completed['history']))
        self.action(order["id"],"complete",409)
        from models.inventory_balance_model import InventoryBalance
        from models.production_record_model import ProductionRecord
        with Session(self.engine) as db:
            self.assertEqual(db.get(InventoryBalance,UUID(self.material_id)).quantity_on_hand,Decimal("6"))
            self.assertEqual(len(list(db.scalars(select(ProductionRecord)))),1)

    def test_product_material_aggregation_and_labor_are_counted_once(self):
        response=self.client.post("/api/v1/products",json={"sku":"ORD-P","name":"Bouquet","selling_price":30000,"assembly_labor_cost":100,"bom":{"flowers":[{"flower_id":self.flower_id,"quantity_required":"2"}],"materials":[{"material_id":self.material_id,"quantity_required":"1","unit":"pcs"}]}})
        self.assertEqual(response.status_code,201,response.text)
        order=self.create_order(items=[{"product_id":response.json()["id"],"quantity":3}])
        from models.user_model import User
        from use_cases.inventory.move_stock import move_stock
        with Session(self.engine) as db:
            move_stock(db,SimpleNamespace(user=db.get(User,UUID(self.staff_id))),[{"material_id":UUID(self.material_id),"quantity_delta":Decimal("20"),"unit_cost":Decimal("100")}],"adjustment",UUID(order["id"]))
            db.commit()
        self.action(order["id"],"confirm")
        self.action(order["id"],"start-production")
        ready=self.action(order["id"],"complete-production").json()
        self.assertEqual(Decimal(ready["production"]["actual_material_cost"]),Decimal("1500"))
        self.assertEqual(Decimal(ready["production"]["labor_cost_snapshot"]),Decimal("3300"))
        from models.inventory_balance_model import InventoryBalance
        from models.inventory_movement_model import InventoryMovement
        with Session(self.engine) as db:
            self.assertEqual(db.get(InventoryBalance,UUID(self.material_id)).quantity_on_hand,Decimal("5"))
            movements=list(db.scalars(select(InventoryMovement).where(InventoryMovement.reference_type=="production")))
            self.assertEqual(len(movements),1)
            self.assertEqual(movements[0].quantity_delta,Decimal("-15"))

    def test_insufficient_second_material_rolls_back_entire_production(self):
        response=self.client.post("/api/v1/materials",json={"sku":"ORD-M2","name":"Second material","base_unit":"pcs"})
        self.assertEqual(response.status_code,201,response.text)
        second_id=response.json()["id"]
        changed=self.client.put(f"/api/v1/flowers/{self.flower_id}/bom",json={"materials":[{"material_id":self.material_id,"quantity_required":"2","unit":"pcs"},{"material_id":second_id,"quantity_required":"1","unit":"pcs"}]})
        self.assertEqual(changed.status_code,200,changed.text)
        order=self.create_order()
        from models.user_model import User
        from use_cases.inventory.move_stock import move_stock
        with Session(self.engine) as db:
            move_stock(db,SimpleNamespace(user=db.get(User,UUID(self.staff_id))),[{"material_id":UUID(self.material_id),"quantity_delta":Decimal("10"),"unit_cost":Decimal("100")}],"adjustment",UUID(order["id"]))
            db.commit()
        self.action(order["id"],"confirm")
        self.action(order["id"],"start-production")
        self.action(order["id"],"complete-production",409)
        from models.inventory_balance_model import InventoryBalance
        from models.inventory_movement_model import InventoryMovement
        from models.production_record_model import ProductionRecord
        from models.order_model import Order
        with Session(self.engine) as db:
            self.assertEqual(db.get(InventoryBalance,UUID(self.material_id)).quantity_on_hand,Decimal("10"))
            self.assertEqual(db.get(InventoryBalance,UUID(second_id)).quantity_on_hand,Decimal("0"))
            self.assertEqual(list(db.scalars(select(InventoryMovement).where(InventoryMovement.reference_type=="production"))),[])
            self.assertEqual(list(db.scalars(select(ProductionRecord))),[])
            self.assertEqual(db.get(Order,UUID(order["id"])).status,"in_production")

    def test_cancel_and_invalid_transitions_preserve_stock(self):
        order=self.create_order()
        self.action(order["id"],"start-production",409)
        self.action(order["id"],"confirm")
        self.action(order["id"],"start-production")
        self.assertEqual(self.action(order["id"],"cancel").json()["status"],"cancelled")
        self.action(order["id"],"start-production",409)
