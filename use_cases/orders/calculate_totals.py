from use_cases.common.validation import money


def calculate_totals(items, discount_amount: int, shipping_charge: int) -> tuple[int, int]:
    subtotal = money(sum(money(item["unit_price"]) * item["quantity"] for item in items))
    total = money(subtotal + money(shipping_charge) - money(discount_amount))
    return subtotal, total
