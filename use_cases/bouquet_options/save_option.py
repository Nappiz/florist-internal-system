from fastapi import HTTPException
from crud import bouquet_options_crud
from models.bouquet_option_material_model import BouquetOptionMaterial
from use_cases.catalogue.validation import normalize_materials

def save_option(db,row,data):
    if data.min_quantity>data.max_quantity: raise HTTPException(422,"Batas jumlah opsi tidak valid.")
    materials=normalize_materials(db,data.materials)
    for key,value in data.model_dump(mode="json",exclude={"materials"}).items(): setattr(row,key,value)
    bouquet_options_crud.replace_materials(db,row.id,[BouquetOptionMaterial(bouquet_option_id=row.id,**line) for line in materials])
