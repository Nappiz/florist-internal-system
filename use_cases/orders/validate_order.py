from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import HTTPException

BUSINESS_TIMEZONE = ZoneInfo("Asia/Jakarta")
REQUIRED_FIELDS = {"customer_name", "sales_channel", "fulfillment_method", "order_date", "discount_amount", "shipping_charge", "items"}


def today():
    return datetime.now(BUSINESS_TIMEZONE).date()


def validate_order(values):
    if any(values[key] is None for key in REQUIRED_FIELDS & values.keys()):
        raise HTTPException(422, "Field wajib order tidak boleh null.")
    if values["order_date"] > today():
        raise HTTPException(422, "Tanggal order tidak boleh di masa depan.")
    if values.get("required_date") is not None and values["required_date"] < values["order_date"]:
        raise HTTPException(422, "Tanggal kebutuhan tidak boleh mendahului tanggal order.")
    if values["fulfillment_method"] == "delivery" and not (values.get("customer_address") or "").strip():
        raise HTTPException(422, "Alamat customer wajib untuk pengiriman.")


def payment_status(total, paid):
    return "paid" if paid >= total else "partial" if paid else "unpaid"
