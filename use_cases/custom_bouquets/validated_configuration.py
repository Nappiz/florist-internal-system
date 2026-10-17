from uuid import UUID
from fastapi import HTTPException
from models.flower_model import Flower
from models.bouquet_option_model import BouquetOption
from models.material_model import Material
from use_cases.custom_bouquets.get_bouquet import get_bouquet
from use_cases.common.validation import require_active

def validated_configuration(db,identity):
    row=get_bouquet(db,identity,lock=True)
    if row.status!="finalized" or row.final_price is None:
        raise HTTPException(409,"Order memerlukan konfigurasi custom finalized.")
    recipe=row.recipe_snapshot
    if not recipe.get("flowers") or not recipe.get("materials"):
        raise HTTPException(422,"Konfigurasi custom belum memiliki resep produksi.")
    for line in sorted(recipe["flowers"],key=lambda line:line["flower_id"]): require_active(db,Flower,UUID(line["flower_id"]))
    for line in sorted(recipe["options"],key=lambda line:line["bouquet_option_id"]): require_active(db,BouquetOption,UUID(line["bouquet_option_id"]))
    for line in sorted(recipe["materials"],key=lambda line:line["material_id"]):
        material=require_active(db,Material,UUID(line["material_id"]))
        if line["unit"]!=material.base_unit: raise HTTPException(409,"Satuan snapshot custom tidak sesuai material.")
    return row
