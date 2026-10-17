from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ReportQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date_from: date | None = None
    date_to: date | None = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0, le=1_000_000)


class DashboardQuery(ReportQuery):
    limit: int = Field(10, ge=1, le=20)


class Period(BaseModel):
    date_from: date
    date_to: date
    timezone: str = "Asia/Jakarta"
    inclusive: bool = True


class PurchaseReport(BaseModel):
    period: Period
    date_basis: str = "purchase_date; received purchases only"
    material_amount_basis: str = "base-unit quantities and item subtotals before purchase discount and shipping"
    purchase_count: int
    total_amount: int
    by_supplier: list[dict]
    top_materials: list[dict]
    top_limit: int


class SalesReport(BaseModel):
    period: Period
    sales_date_basis: str = "completed_at in Asia/Jakarta; completed orders only; sales include customer shipping"
    collections_date_basis: str = "payment_date; all recorded payments including cancelled orders; refunds unsupported"
    item_amount_basis: str = "item subtotal before order discount and customer shipping"
    completed_order_count: int
    completed_sales_total: int
    order_count: int
    order_count_date_basis: str = "order_date; all statuses"
    orders_by_status: dict[str, int]
    collections_total: int
    collections_from_cancelled_orders: int
    by_sales_channel: list[dict]
    top_items: list[dict]
    top_limit: int


class InventoryReport(BaseModel):
    period: Period
    as_of: datetime
    valuation_basis: str = "current balances at moving average cost; period applies to movement counts only"
    inventory_value: Decimal | None
    known_inventory_value: Decimal
    valuation_complete: bool
    missing_cost_material_count: int
    low_stock_count: int
    low_stock: list[dict]
    movements_by_type: dict[str, int]
    items: list[dict]
    total: int
    limit: int
    offset: int


class ProfitabilityReport(BaseModel):
    period: Period
    revenue_basis: str = "completed orders by Jakarta completion date; subtotal minus discount; customer shipping excluded"
    margin_basis: str = "gross margin; revenue minus snapshotted direct production cost; not net profit"
    actual_cost_date_basis: str = "production record created_at in Asia/Jakarta; includes costs for subsequently cancelled orders"
    completed_revenue_excluding_shipping: int
    completed_production_cost: Decimal
    completed_order_count: int
    missing_production_cost_count: int
    cost_complete: bool
    gross_margin: Decimal | None
    gross_margin_percent: Decimal | None
    actual_production_cost: Decimal
    estimated_product_hpp: list[dict]
    estimate_basis: str = "current active product recipes and current inventory or listing reference costs"
    products_total: int
    limit: int
    offset: int


class DashboardReport(BaseModel):
    period: Period
    active_orders: int
    awaiting_production: int
    ready_for_fulfillment: int
    completed_orders: int
    completed_sales_total: int
    collections_total: int
    received_purchases_total: int
    inventory_value: Decimal | None
    low_stock_count: int
    low_stock: list[dict]
    order_status_counts: dict[str, int]
    purchase_status_counts: dict[str, int]
    status_count_basis: str = "business order_date and purchase_date in selected period; all statuses"
    recent_basis: str = "most recently created records within selected business-date period"
    recent_orders: list[dict]
    recent_purchases: list[dict]
    limit: int


class RecentRecords(BaseModel):
    period: Period
    items: list[dict]
    limit: int
