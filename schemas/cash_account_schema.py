from datetime import date, datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, Field
from schemas.catalogue_types import InputModel, Money, Name


class CashAccountCreate(InputModel):
    operation_key: UUID
    name: Name
    account_type: Literal['cash', 'bank', 'e_wallet']
    opening_balance: Money = 0
    opening_date: date
    history_mode: Literal['opening', 'backfill'] = 'opening'
    reason: str = Field(min_length=1, max_length=2000)


class CashAccountUpdate(InputModel):
    operation_key: UUID
    name: Name | None = None
    is_active: bool | None = None
    reason: str = Field(min_length=1, max_length=2000)


class CashAccountQuery(InputModel):
    is_active: bool | None = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0, le=1_000_000)


class CashAccountOption(BaseModel):
    id: UUID
    name: str
    account_type: Literal['cash', 'bank', 'e_wallet']


class CashAccountResponse(CashAccountOption):
    opening_date: date
    history_mode: Literal['opening', 'backfill']
    is_active: bool
    created_by: UUID | None
    created_at: datetime
    balance: int
    currency: Literal['IDR'] = 'IDR'
