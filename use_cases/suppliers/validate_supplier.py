from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import HTTPException

BUSINESS_TIMEZONE = ZoneInfo("Asia/Jakarta")
REQUIRED_FIELDS = {"material_name", "store_name", "purchase_url", "price", "pack_quantity", "unit", "last_checked_at"}


def validate_supplier(values: dict) -> dict:
    if any(values.get(field) is None for field in REQUIRED_FIELDS & values.keys()):
        raise HTTPException(422, "Field wajib supplier tidak boleh null.")
    checked_at = values.get("last_checked_at")
    if checked_at is not None and checked_at > datetime.now(BUSINESS_TIMEZONE).date():
        raise HTTPException(422, "Tanggal cek harga tidak boleh di masa depan.")
    if "purchase_url" in values:
        values["purchase_url"] = str(values["purchase_url"])
    if "unit" in values:
        values["unit"] = values["unit"].lower()
    return values
