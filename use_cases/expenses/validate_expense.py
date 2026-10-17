from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import HTTPException

BUSINESS_TIMEZONE = ZoneInfo("Asia/Jakarta")
REQUIRED_FIELDS = {"supplier_id", "purchase_date", "pack_count", "price_per_pack", "shipping_cost", "discount_amount"}


def validate_expense(values: dict) -> None:
    if any(values[field] is None for field in REQUIRED_FIELDS & values.keys()):
        raise HTTPException(422, "Field wajib expense tidak boleh null.")
    purchase_date = values.get("purchase_date")
    if purchase_date is not None and purchase_date > datetime.now(BUSINESS_TIMEZONE).date():
        raise HTTPException(422, "Tanggal pembelian tidak boleh di masa depan.")
