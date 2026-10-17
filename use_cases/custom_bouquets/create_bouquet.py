from uuid import uuid4
from crud import custom_bouquets_crud
from models.custom_bouquet_model import CustomBouquet
from use_cases.custom_bouquets.estimate import estimate
from use_cases.custom_bouquets.save_configuration import save_configuration
from use_cases.audit.record import record
from use_cases.common.persistence import finish,flush

def create_bouquet(db,actor,data,*,duplicated_from=None):
    result=estimate(db,data)
    identity=uuid4()
    row=custom_bouquets_crud.add(db,CustomBouquet(id=identity,configuration_number="CBB-"+identity.hex.upper(),name=data.name or "Custom Bouquet",status="draft",proposed_price=result["proposed_price"],recipe_snapshot={},created_by=actor.user.id,updated_by=actor.user.id))
    flush(db)
    save_configuration(db,actor,row,data,result)
    record(db,actor,"create","custom_bouquet",row.id)
    if duplicated_from is not None: record(db,actor,"duplicate","custom_bouquet",row.id,{"source_configuration_id":str(duplicated_from)})
    finish(db)
    return row
