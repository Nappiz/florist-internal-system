from uuid import uuid4
from crud import bouquet_options_crud
from models.bouquet_option_model import BouquetOption
from use_cases.custom_bouquets.permissions import require_superadmin
from use_cases.bouquet_options.save_option import save_option
from use_cases.bouquet_options.option_response import option_response
from use_cases.audit.record import record
from use_cases.common.persistence import finish,flush

def create_option(db,actor,data):
    require_superadmin(actor)
    row=bouquet_options_crud.add(db,BouquetOption(id=uuid4(),**data.model_dump(mode="json",exclude={"materials"})))
    flush(db)
    save_option(db,row,data)
    record(db,actor,"create","bouquet_option",row.id)
    finish(db)
    return option_response(db,row)
