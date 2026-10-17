from sqlalchemy import select
from models.bouquet_setting_model import BouquetSetting

def get(db,*,lock=False):
    query=select(BouquetSetting).where(BouquetSetting.id==1)
    return db.scalar(query.with_for_update() if lock else query)

def add(db,row):
    db.add(row)
    return row
