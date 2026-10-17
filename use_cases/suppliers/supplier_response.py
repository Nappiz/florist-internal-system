from decimal import Decimal, ROUND_HALF_UP

from models.supplier_model import Supplier
from schemas.supplier_schema import SupplierResponse


def supplier_response(supplier: Supplier) -> SupplierResponse:
    values = {
        field: getattr(supplier, field)
        for field in SupplierResponse.model_fields
        if field not in {"currency", "unit_price", "landed_unit_price"}
    }
    values["unit_price"] = (supplier.price / supplier.pack_quantity).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    values["landed_unit_price"] = None
    if supplier.estimated_shipping_cost is not None:
        values["landed_unit_price"] = (
            (supplier.price + supplier.estimated_shipping_cost) / supplier.pack_quantity
        ).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    return SupplierResponse(**values)
