from collections import defaultdict
from decimal import Decimal
from fastapi import HTTPException
from crud import flowers_crud,bouquet_options_crud
from models.flower_model import Flower
from models.bouquet_option_model import BouquetOption
from models.inventory_balance_model import InventoryBalance
from models.material_model import Material
from use_cases.catalogue.costing import material_cost
from use_cases.catalogue.precision import cost_precision
from use_cases.common.validation import require_active,money,quantity
from use_cases.bouquet_settings.get_settings import get_settings
from use_cases.orders.snapshot_order import snapshot_cost

@cost_precision()
def estimate(db,data,*,finalizing=False):
    settings=get_settings(db)
    selected_flowers=defaultdict(int)
    selected_options=defaultdict(int)
    for line in data.flowers: selected_flowers[line.flower_id]+=line.quantity
    for line in data.options: selected_options[line.bouquet_option_id]+=line.quantity
    stems=sum(selected_flowers.values())
    if stems>settings.max_stems or ((stems or finalizing) and stems<settings.min_stems):
        raise HTTPException(422,"Jumlah tangkai tidak sesuai batas pengaturan.")
    quantities=defaultdict(Decimal)
    units={}
    flowers=[]
    options=[]
    missing=[]
    labor=Decimal(settings.assembly_labor_cost)
    price=settings.assembly_fee
    def add_material(identity,amount,unit):
        material=require_active(db,Material,identity)
        if unit!=material.base_unit: raise HTTPException(422,"Satuan resep tidak sesuai material.")
        if identity in units and units[identity]!=unit: raise HTTPException(422,"Satuan material tidak konsisten.")
        units[identity]=unit
        quantities[identity]+=Decimal(amount)
    # Match catalogue lock order: flowers/options precede materials.
    flower_rows={identity:require_active(db,Flower,identity) for identity in sorted(selected_flowers,key=str)}
    option_rows={identity:require_active(db,BouquetOption,identity) for identity in sorted(selected_options,key=str)}
    raw_materials=[]
    flower_materials={}
    for identity,count in sorted(selected_flowers.items(),key=lambda row:str(row[0])):
        flower=flower_rows[identity]
        rows=flowers_crud.materials(db,identity)
        flower_materials[str(identity)]=rows
        if not rows: missing.append({"type":"flower","id":str(identity),"reason":"missing_material_mapping"})
        raw_materials.extend((row.material_id,row.quantity_required*count,row.unit) for row in rows)
        labor+=Decimal(flower.estimated_labor_cost)*count
        price+=flower.selling_price*count
        flowers.append({"flower_id":str(identity),"name":flower.name,"image_url":flower.image_url,"quantity":count,"unit_price":flower.selling_price,"estimated_labor_cost":flower.estimated_labor_cost,"subtotal":money(flower.selling_price*count)})
    for identity,count in sorted(selected_options.items(),key=lambda row:str(row[0])):
        option=option_rows[identity]
        if count<option.min_quantity or count>option.max_quantity: raise HTTPException(422,"Jumlah opsi tidak sesuai batas opsi.")
        rows=bouquet_options_crud.materials(db,identity)
        if option.requires_materials and not rows: missing.append({"type":"option","id":str(identity),"reason":"missing_material_mapping"})
        raw_materials.extend((row.material_id,row.quantity_required*count,row.unit) for row in rows)
        price+=option.selling_price*count
        options.append({"bouquet_option_id":str(identity),"name":option.name,"option_group":option.option_group,"image_url":option.image_url,"quantity":count,"unit_price":option.selling_price,"subtotal":money(option.selling_price*count)})
    raw_materials.extend((row.material_id,row.quantity_required,row.unit) for row in data.additional_materials)
    for identity,amount,unit in sorted(raw_materials,key=lambda row:str(row[0])): add_material(identity,amount,unit)
    materials=[]
    known_cost=labor
    complete=bool(stems) and not missing
    for identity,amount in sorted(quantities.items(),key=lambda row:str(row[0])):
        amount=quantity(amount)
        cost=material_cost(db,identity)
        balance=db.get(InventoryBalance,identity)
        stock=Decimal(balance.quantity_on_hand) if balance else Decimal(0)
        if cost["unit_cost"] is None:
            complete=False
            missing.append({"type":"material","id":str(identity),"reason":"missing_cost"})
        else: known_cost+=amount*cost["unit_cost"]
        materials.append({"material_id":str(identity),"quantity":amount,"unit":units[identity],"unit_cost":cost["unit_cost"],"cost_source":cost["source"],"current_stock":stock,"shortage_quantity":max(Decimal(0),amount-stock)})
    cost_by_id={line["material_id"]:line["unit_cost"] for line in materials}
    for line in flowers:
        rows=flower_materials[line["flower_id"]]
        flower_complete=bool(rows) and all(cost_by_id[str(row.material_id)] is not None for row in rows)
        flower_hpp=Decimal(line["estimated_labor_cost"])
        if flower_complete: flower_hpp+=sum((row.quantity_required*cost_by_id[str(row.material_id)] for row in rows),Decimal(0))
        line["estimated_hpp"]=snapshot_cost(flower_hpp) if flower_complete else None
    proposed=max(money(price),settings.minimum_price)
    hpp=snapshot_cost(known_cost) if complete else None
    profit=Decimal(proposed)-hpp if hpp is not None else None
    return {"flowers":flowers,"options":options,"additional_materials":[row.model_dump(mode="json") for row in data.additional_materials],"materials":materials,"labor_cost":snapshot_cost(labor),"assembly_fee":settings.assembly_fee,"assembly_labor_cost":Decimal(settings.assembly_labor_cost),"stem_count":stems,"proposed_price":proposed,"estimated_hpp":hpp,"known_material_and_labor_cost":snapshot_cost(known_cost),"cost_complete":complete,"gross_profit":profit,"gross_margin":(profit/Decimal(proposed)*100 if profit is not None and proposed else None),"availability":"unknown" if missing or not stems else ("insufficient_stock" if any(row["shortage_quantity"]>0 for row in materials) else "available"),"incomplete_reasons":missing,"pricing_version":settings.pricing_version,"personalization":data.personalization.model_dump()}
