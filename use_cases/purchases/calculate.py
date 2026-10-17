from fastapi import HTTPException
from use_cases.common.validation import money


def calculate(purchase,items):
    purchase.subtotal=money(sum(item.subtotal for item in items))
    purchase.total_amount=money(purchase.subtotal+purchase.shipping_cost-purchase.discount_amount)
    return purchase.total_amount
