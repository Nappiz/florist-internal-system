from decimal import Decimal
from fastapi import HTTPException
from use_cases.custom_bouquets.get_bouquet import get_bouquet
from use_cases.custom_bouquets.estimate import estimate
from use_cases.custom_bouquets.save_configuration import save_configuration
from use_cases.custom_bouquets.configuration_input import configuration_input
from use_cases.custom_bouquets.permissions import require_superadmin
from use_cases.audit.record import record
from use_cases.common.persistence import finish
from use_cases.orders.snapshot_order import json_snapshot

def finalize_bouquet(db,actor,identity,data):
    row=get_bouquet(db,identity,lock=True)
    if row.status!="draft": raise HTTPException(409,"Hanya draft dapat difinalisasi.")
    if data.final_price is not None:
        require_superadmin(actor)
        if not data.reason: raise HTTPException(422,"Alasan perubahan harga wajib diisi.")
    config=configuration_input(row)
    result=estimate(db,config,finalizing=True)
    if any(line["reason"]=="missing_material_mapping" for line in result["incomplete_reasons"]):
        raise HTTPException(422,"Lengkapi mapping material sebelum finalisasi.")
    save_configuration(db,actor,row,config,result)
    row.final_price=result["proposed_price"] if data.final_price is None else data.final_price
    row.price_override_reason=data.reason if data.final_price is not None else None
    row.status="finalized"
    snapshot=dict(row.recipe_snapshot)
    hpp=result["estimated_hpp"]
    snapshot.update(final_price=row.final_price,price_override_reason=row.price_override_reason,gross_profit=Decimal(row.final_price)-hpp if hpp is not None else None,gross_margin=((Decimal(row.final_price)-hpp)/row.final_price*100 if hpp is not None and row.final_price else None))
    row.recipe_snapshot=json_snapshot(snapshot)
    if data.final_price is not None: record(db,actor,"price_override","custom_bouquet",row.id,{"reason":data.reason,"proposed_price":result["proposed_price"],"final_price":row.final_price})
    record(db,actor,"finalize","custom_bouquet",row.id)
    finish(db)
    return row
