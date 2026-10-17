from decimal import Decimal

from fastapi import HTTPException


def calculate_expense(pack_count: int, price_per_pack: Decimal, shipping_cost: Decimal, discount_amount: Decimal):
    subtotal = (price_per_pack * pack_count).quantize(Decimal("0.01"))
    total = subtotal + shipping_cost - discount_amount
    if not (Decimal("0") <= subtotal <= Decimal("999999999999999999.99")):
        raise HTTPException(422, "Subtotal pembelian melebihi batas pencatatan.")
    if not (Decimal("0") <= total <= Decimal("999999999999999999.99")):
        raise HTTPException(422, "Total pembelian tidak boleh negatif atau melebihi batas pencatatan.")
    return subtotal, total.quantize(Decimal("0.01"))
