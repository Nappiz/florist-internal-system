from decimal import Decimal
from typing import Annotated
from pydantic import ConfigDict,Field
from schemas.custom_bouquet_schema import Input,Money,Count

class BouquetSettingsInput(Input):
    min_stems: Count=1
    max_stems: Count=1000
    minimum_price: Money=0
    assembly_fee: Money=0
    assembly_labor_cost: Annotated[Decimal,Field(ge=0,le=Decimal("999999999999999"),decimal_places=8,allow_inf_nan=False)]=Decimal(0)

class BouquetSettingsResponse(BouquetSettingsInput):
    model_config=ConfigDict(from_attributes=True)
    pricing_version: int
