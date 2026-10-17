from schemas.bouquet_option_schema import BouquetOptionResponse
from crud import bouquet_options_crud

def option_response(db,row):
    values={key:getattr(row,key) for key in BouquetOptionResponse.model_fields if key!="materials"}
    values["materials"]=[{"material_id":line.material_id,"quantity_required":line.quantity_required,"unit":line.unit} for line in bouquet_options_crud.materials(db,row.id)]
    return BouquetOptionResponse(**values)
