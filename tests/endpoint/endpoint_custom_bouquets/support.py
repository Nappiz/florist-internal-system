from sqlalchemy.orm import Session
from tests.helpers.auth import AuthEndpointTestCase
from tests.unit.test_custom_bouquets import support as model_registration

class BouquetEndpointCase(AuthEndpointTestCase):
    def setUp(self):
        super().setUp()
        from routes.custom_bouquets import router
        from routes.bouquet_options import router as options
        from routes.bouquet_settings import router as settings
        from routes.orders import router as orders
        self.app.include_router(router,prefix="/bouquet-test")
        self.app.include_router(options,prefix="/bouquet-test")
        self.app.include_router(settings,prefix="/bouquet-test")
        self.app.include_router(orders,prefix="/bouquet-test")
        self.login_as("staff")
        from models.material_model import Material
        from models.flower_model import Flower
        from models.flower_material_model import FlowerMaterial
        from models.inventory_balance_model import InventoryBalance
        with Session(self.engine) as db:
            material=Material(sku="CBB-M",name="Pipe",base_unit="pcs")
            flower=Flower(sku="CBB-F",name="Rose",selling_price=10000,estimated_labor_cost=10)
            db.add_all([material,flower]);db.flush()
            db.add_all([FlowerMaterial(flower_id=flower.id,material_id=material.id,quantity_required=2,unit="pcs"),InventoryBalance(material_id=material.id,quantity_on_hand=100,average_unit_cost=4,has_received_cost=True)])
            db.commit()
            self.flower_id=str(flower.id);self.material_id=str(material.id)
        self.payload={"name":"Gift roses","flowers":[{"flower_id":self.flower_id,"quantity":3}],"personalization":{"recipient_name":"B","gift_message":"Hello"}}

    def create_bouquet(self):
        response=self.client.post("/bouquet-test/custom-bouquets",json=self.payload)
        self.assertEqual(response.status_code,201,response.text)
        return response.json()

    def finalized_bouquet(self):
        row=self.create_bouquet()
        response=self.client.post(f"/bouquet-test/custom-bouquets/{row['id']}/finalize",json={})
        self.assertEqual(response.status_code,200,response.text)
        return response.json()
