from decimal import Decimal
from uuid import uuid4
from fastapi import HTTPException
from models.flower_model import Flower
from models.product_model import Product
from models.order_item_model import OrderItem
from use_cases.common.validation import money,require_active
from use_cases.custom_bouquets.validated_configuration import validated_configuration
from use_cases.custom_bouquets.permissions import require_superadmin
from use_cases.audit.record import record
from use_cases.orders.lock_references import lock_references
from use_cases.orders.snapshot_order import json_snapshot

def validate_custom_order_price(actor,items,discount_amount,price_override_reason=None):
    if any(line.custom_bouquet_id is not None for line in items) and discount_amount:
        require_superadmin(actor)
        if not price_override_reason: raise HTTPException(422,"Alasan diskon order custom wajib diisi.")

def build_items(db,order_id,data,*,actor=None,discount_amount=0,price_override_reason=None):
    validate_custom_order_price(actor,data,discount_amount,price_override_reason)
    lock_references(db,data)
    references={("custom" if line.custom_bouquet_id else "product" if line.product_id else "flower",line.custom_bouquet_id or line.product_id or line.flower_id) for line in data}
    locked={}
    # All callers use the same order for configuration/catalogue locks.
    for kind,identity in sorted(references,key=lambda key:({"custom":0,"product":1,"flower":2}[key[0]],str(key[1]))):
        locked[kind,identity]=validated_configuration(db,identity) if kind=="custom" else require_active(db,Product if kind=="product" else Flower,identity)
    items=[]
    for position,line in enumerate(data):
        kind="custom" if line.custom_bouquet_id else "product" if line.product_id else "flower"
        catalogue=locked[kind,line.custom_bouquet_id or line.product_id or line.flower_id]
        default_price=catalogue.final_price if kind=="custom" else catalogue.selling_price
        if kind=="custom" and line.unit_price is not None:
            require_superadmin(actor)
            if not line.price_override_reason: raise HTTPException(422,"Alasan perubahan harga item custom wajib diisi.")
            record(db,actor,"price_override","order",order_id,{"custom_bouquet_id":str(catalogue.id),"reason":line.price_override_reason,"proposed_price":default_price,"final_price":line.unit_price})
        price=money(default_price if line.unit_price is None else line.unit_price)
        item=OrderItem(id=uuid4(),order_id=order_id,position=position,flower_id=line.flower_id,product_id=line.product_id,custom_bouquet_id=line.custom_bouquet_id,item_type={"custom":"CUSTOM_BOUQUET","product":"PRODUCT","flower":"FLOWER"}[kind],item_name_snapshot=catalogue.name,quantity=line.quantity,unit_price=price,subtotal=money(price*line.quantity))
        if kind=="custom":
            recipe={**catalogue.recipe_snapshot,"configuration_id":str(catalogue.id),"configuration_number":catalogue.configuration_number,"personalization":dict(catalogue.personalization),"order_unit_price":price,"order_price_override_reason":line.price_override_reason}
            hpp=catalogue.estimated_hpp
            recipe["gross_profit"]=Decimal(price)-hpp if hpp is not None else None
            recipe["gross_margin"]=((Decimal(price)-hpp)/price*100 if hpp is not None and price else None)
            item.recipe_snapshot=json_snapshot(recipe)
            from use_cases.orders.snapshot_order import snapshot_cost
            item.labor_cost_snapshot=snapshot_cost(item.recipe_snapshot["labor_cost"])
            item.estimated_hpp_snapshot=snapshot_cost(item.recipe_snapshot["estimated_hpp"])
            item.cost_complete=item.recipe_snapshot["cost_complete"]
        items.append(item)
    return items
