from crud import bouquet_settings_crud
from models.bouquet_setting_model import BouquetSetting

def get_settings(db):
    return bouquet_settings_crud.get(db) or BouquetSetting(id=1,min_stems=1,max_stems=1000,minimum_price=0,assembly_fee=0,assembly_labor_cost=0,pricing_version=1)
