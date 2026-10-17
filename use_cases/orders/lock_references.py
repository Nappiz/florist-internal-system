from uuid import UUID
from fastapi import HTTPException
from crud import flowers_crud,products_crud
from models.product_model import Product
from models.flower_model import Flower
from models.bouquet_option_model import BouquetOption
from models.material_model import Material
from use_cases.common.validation import require_active
from use_cases.custom_bouquets.get_bouquet import get_bouquet

def lock_references(db,items):
    # Catalogue writers acquire Product -> Flower -> Material. Lock the entire
    # union once so mixed standard/custom orders cannot reverse those locks.
    product_ids={item.product_id for item in items if item.product_id}
    custom_ids={item.custom_bouquet_id for item in items if item.custom_bouquet_id}
    flowers={item.flower_id for item in items if item.flower_id}
    options=set()
    materials=set()
    for identity in sorted(product_ids,key=str):
        require_active(db,Product,identity)
        flowers.update(line.flower_id for line in products_crud.flowers(db,identity))
        materials.update(line.material_id for line in products_crud.materials(db,identity))
    for identity in sorted(custom_ids,key=str):
        config=get_bouquet(db,identity,lock=True)
        if config.status!="finalized" or config.final_price is None:
            raise HTTPException(409,"Order memerlukan konfigurasi custom finalized.")
        flowers.update(UUID(line["flower_id"]) for line in config.recipe_snapshot.get("flowers",[]))
        options.update(UUID(line["bouquet_option_id"]) for line in config.recipe_snapshot.get("options",[]))
        materials.update(UUID(line["material_id"]) for line in config.recipe_snapshot.get("materials",[]))
    for identity in sorted(flowers,key=str):
        require_active(db,Flower,identity)
        materials.update(line.material_id for line in flowers_crud.materials(db,identity))
    for identity in sorted(options,key=str): require_active(db,BouquetOption,identity)
    for identity in sorted(materials,key=str): require_active(db,Material,identity)
