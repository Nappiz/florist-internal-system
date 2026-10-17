from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

Money = Annotated[int, Field(strict=True, ge=0, le=999999999999999)]
Count = Annotated[int, Field(strict=True, ge=1, le=1000000)]
OrderStatus = Literal["draft", "confirmed", "in_production", "ready", "completed", "cancelled"]
PaymentStatus = Literal["unpaid", "partial", "paid"]
Channel = Literal["instagram", "whatsapp", "tiktok", "campus_group", "referral", "offline", "other"]
Phone=Annotated[str,Field(min_length=7,max_length=40,pattern=r'^\+?(?:[0-9][ ()-]*){6,14}[0-9]$')]


class OrderInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class OrderItemInput(OrderInput):
    flower_id: UUID | None = None
    product_id: UUID | None = None
    custom_bouquet_id: UUID | None = None
    price_override_reason: str | None = Field(default=None,min_length=1,max_length=2000)
    quantity: Count = 1
    unit_price: Money | None = None

    @model_validator(mode="after")
    def exactly_one_reference(self):
        if sum(value is not None for value in (self.flower_id,self.product_id,self.custom_bouquet_id)) != 1:
            raise ValueError("Pilih tepat satu bunga, produk, atau buket custom.")
        if "unit_price" in self.model_fields_set and self.unit_price is None:
            raise ValueError("Harga jual tidak boleh null.")
        return self


class OrderCreate(OrderInput):
    customer_name: str = Field(min_length=1, max_length=150)
    customer_phone: Phone | None = None
    customer_address: str | None = Field(default=None, max_length=2000)
    customer_notes: str | None = Field(default=None, max_length=2000)
    sales_channel: Channel = "other"
    fulfillment_method: Literal["pickup", "delivery"] = "pickup"
    order_date: date | None = None
    required_date: date | None = None
    price_override_reason: str | None = Field(default=None,min_length=1,max_length=2000)
    discount_amount: Money = 0
    shipping_charge: Money = 0
    notes: str | None = Field(default=None, max_length=2000)
    items: list[OrderItemInput] = Field(min_length=1, max_length=100)


class OrderUpdate(OrderInput):
    customer_name: str | None = Field(default=None, min_length=1, max_length=150)
    customer_phone: Phone | None = None
    customer_address: str | None = Field(default=None, max_length=2000)
    customer_notes: str | None = Field(default=None, max_length=2000)
    sales_channel: Channel | None = None
    fulfillment_method: Literal["pickup", "delivery"] | None = None
    order_date: date | None = None
    required_date: date | None = None
    price_override_reason: str | None = Field(default=None,min_length=1,max_length=2000)
    discount_amount: Money | None = None
    shipping_charge: Money | None = None
    notes: str | None = Field(default=None, max_length=2000)
    items: list[OrderItemInput] | None = Field(default=None, min_length=1, max_length=100)


class OrderCancel(OrderInput):
    reason: str | None = Field(default=None, max_length=2000)


class OrderAction(OrderInput):
    pass


class OrderPaymentCreate(OrderInput):
    cash_account_id: UUID
    payment_key: UUID
    payment_date: date | None = None
    amount: Annotated[int, Field(strict=True, gt=0, le=999999999999999)]
    method: str | None = Field(default=None, min_length=1, max_length=50)
    reference_number: str | None = Field(default=None, min_length=1, max_length=100)
    notes: str | None = Field(default=None, max_length=2000)


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    flower_id: UUID | None
    product_id: UUID | None
    custom_bouquet_id: UUID | None
    item_type: str
    item_name_snapshot: str
    quantity: int
    unit_price: int
    subtotal: int
    recipe_snapshot: dict | None
    labor_cost_snapshot: Decimal
    estimated_hpp_snapshot: Decimal | None
    cost_complete: bool


class OrderPaymentResponse(BaseModel):
    cash_account_id: UUID | None
    reversed_at: datetime | None
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    payment_key: UUID
    payment_date: date
    amount: int
    method: str | None
    reference_number: str | None
    notes: str | None
    created_by: UUID | None
    created_at: datetime


class ProductionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    actual_material_cost: Decimal
    labor_cost_snapshot: Decimal
    total_production_cost: Decimal
    created_by: UUID | None
    created_at: datetime


class OrderActivityResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id: UUID
    actor_id: UUID | None
    action: str
    created_at: datetime


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    order_number: str
    customer_name: str
    customer_phone: str | None
    customer_address: str | None
    customer_notes: str | None
    sales_channel: str
    fulfillment_method: str
    order_date: date
    required_date: date | None
    subtotal: int
    discount_amount: int
    shipping_charge: int
    total_amount: int
    status: OrderStatus
    payment_status: PaymentStatus
    paid_amount: int
    remaining_amount: int
    notes: str | None
    cancellation_reason: str | None
    items: list[OrderItemResponse]
    payments: list[OrderPaymentResponse]
    production: ProductionResponse | None
    history: list[OrderActivityResponse]
    created_by: UUID | None
    updated_by: UUID | None
    created_at: datetime
    updated_at: datetime
    confirmed_at: datetime | None
    production_started_at: datetime | None
    ready_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None


class OrderListQuery(OrderInput):
    q: str | None = Field(default=None, min_length=1, max_length=100)
    status: OrderStatus | None = None
    payment_status: PaymentStatus | None = None
    sales_channel: Channel | None = None
    date_from: date | None = None
    date_to: date | None = None
    required_date: date | None = None
    sort: Literal["newest", "oldest", "required_date", "total_asc", "total_desc"] = "newest"
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0, le=1000000)


class OrderPage(BaseModel):
    items: list[OrderResponse]
    total: int
    limit: int
    offset: int
