from decimal import Decimal
from types import SimpleNamespace
from sqlalchemy import create_engine,event
from sqlalchemy.orm import Session
import models
from models.base import Base
from models.bouquet_setting_model import BouquetSetting
from models.bouquet_option_model import BouquetOption
from models.bouquet_option_material_model import BouquetOptionMaterial
from models.custom_bouquet_model import CustomBouquet
from models.custom_bouquet_flower_model import CustomBouquetFlower
from models.custom_bouquet_option_model import CustomBouquetOption
from models.custom_bouquet_material_model import CustomBouquetMaterial
from models.material_model import Material
from models.inventory_balance_model import InventoryBalance
from models.flower_model import Flower
from models.flower_material_model import FlowerMaterial
from models.user_model import User
from schemas.custom_bouquet_schema import BouquetCreate

def setup_bouquet(case):
    engine=create_engine("sqlite://")
    event.listen(engine,"connect",lambda conn,_:conn.execute("PRAGMA foreign_keys=ON"))
    Base.metadata.create_all(engine)
    case.addCleanup(engine.dispose)
    case.db=Session(engine)
    case.addCleanup(case.db.close)
    db=case.db
    staff=User(username="customstaff",password_hash="test")
    admin=User(username="customadmin",password_hash="test",role="superadmin",is_superadmin=True)
    material=Material(sku="CUSTOM-M",name="Pipe",base_unit="pcs")
    flower=Flower(sku="CUSTOM-F",name="Rose",selling_price=10000,estimated_labor_cost=10)
    option=BouquetOption(name="Wrap",option_group="wrapping",selling_price=500)
    settings=BouquetSetting(id=1,min_stems=1,max_stems=1000,minimum_price=0,assembly_fee=100,assembly_labor_cost=20,pricing_version=1)
    db.add_all([staff,admin,material,flower,option,settings]);db.flush()
    db.add_all([InventoryBalance(material_id=material.id,quantity_on_hand=7,average_unit_cost=4,has_received_cost=True),FlowerMaterial(flower_id=flower.id,material_id=material.id,quantity_required=2,unit="pcs"),BouquetOptionMaterial(bouquet_option_id=option.id,material_id=material.id,quantity_required=1,unit="pcs")]);db.commit()
    case.staff=SimpleNamespace(user=staff)
    case.admin=SimpleNamespace(user=admin)
    case.material=material;case.flower=flower;case.option=option;case.settings=settings;case.balance_model=InventoryBalance
    case.data=BouquetCreate(name="Custom roses",flowers=[{"flower_id":flower.id,"quantity":1},{"flower_id":flower.id,"quantity":2}],options=[{"bouquet_option_id":option.id,"quantity":2}],additional_materials=[{"material_id":material.id,"quantity_required":"2","unit":"pcs"}],personalization={"gift_message":"Hello"})
