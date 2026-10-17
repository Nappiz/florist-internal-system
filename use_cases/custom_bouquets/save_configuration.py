from datetime import UTC,datetime
from uuid import UUID
from crud import custom_bouquets_crud
from models.custom_bouquet_flower_model import CustomBouquetFlower
from models.custom_bouquet_option_model import CustomBouquetOption
from models.custom_bouquet_material_model import CustomBouquetMaterial
from use_cases.orders.snapshot_order import json_snapshot
from use_cases.catalogue.validation import normalize_materials

def save_configuration(db,actor,row,data,result):
    row.name=data.name or row.configuration_number
    row.customer_reference=data.customer_reference
    row.description=data.description
    row.image_reference=str(data.image_reference) if data.image_reference is not None else None
    row.personalization=data.personalization.model_dump()
    row.estimated_hpp=result["estimated_hpp"]
    row.cost_complete=result["cost_complete"]
    row.proposed_price=result["proposed_price"]
    row.assembly_fee=result["assembly_fee"]
    row.assembly_labor_cost=result["assembly_labor_cost"]
    row.pricing_version=result["pricing_version"]
    row.recipe_snapshot=json_snapshot(result)
    row.updated_by=actor.user.id
    row.updated_at=datetime.now(UTC)
    flowers=[CustomBouquetFlower(custom_bouquet_id=row.id,flower_id=UUID(line["flower_id"]),quantity=line["quantity"],unit_price_snapshot=line["unit_price"],estimated_hpp_snapshot=line["estimated_hpp"]) for line in result["flowers"]]
    options=[CustomBouquetOption(custom_bouquet_id=row.id,bouquet_option_id=UUID(line["bouquet_option_id"]),quantity=line["quantity"],selling_price_snapshot=line["unit_price"]) for line in result["options"]]
    materials=[CustomBouquetMaterial(custom_bouquet_id=row.id,**line) for line in normalize_materials(db,data.additional_materials)]
    custom_bouquets_crud.replace_components(db,row.id,flowers,options,materials)
    return row
