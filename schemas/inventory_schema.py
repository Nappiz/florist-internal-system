from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import Field,AwareDatetime,BaseModel
from schemas.catalogue_types import InputModel


class AdjustmentInput(InputModel):
    adjustment_key: UUID
    material_id: UUID
    quantity_delta: Decimal=Field(allow_inf_nan=False,ge=Decimal('-999999999999.999999'),le=Decimal('999999999999.999999'),decimal_places=6)
    unit_cost: Decimal | None=Field(None,ge=0,le=Decimal('9999999999999999.99999999'),decimal_places=8,allow_inf_nan=False)
    reason: str=Field(min_length=3,max_length=2000,pattern=r'.*\S.*')


class InventoryQuery(InputModel):
    material_id: UUID | None=None
    q: str | None=Field(None,min_length=1,max_length=100)
    date_from: AwareDatetime | None=None
    date_to: AwareDatetime | None=None
    limit: int=Field(20,ge=1,le=100)
    offset: int=Field(0,ge=0,le=1_000_000)


class BalanceResponse(BaseModel):
    material_id: UUID
    quantity_on_hand: Decimal
    average_unit_cost: Decimal
    has_received_cost: bool
    updated_at: datetime


class InventoryResponse(BalanceResponse):
    material_name: str
    sku: str
    base_unit: str
    minimum_stock: Decimal
    is_active: bool
    is_low_stock: bool
    inventory_value: Decimal


class MovementResponse(BaseModel):
    id: UUID
    event_key: str
    material_id: UUID
    movement_type: str
    quantity_delta: Decimal
    unit_cost_snapshot: Decimal
    reference_type: str
    reference_id: UUID
    notes: str | None
    created_by: UUID | None
    created_at: datetime
