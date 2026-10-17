from models.supplier_model import Supplier


def supplier_snapshot(supplier: Supplier) -> dict:
    return {field: getattr(supplier, field) for field in (
        "material_name", "store_name", "purchase_url", "pack_quantity", "unit", "category", "variant", "marketplace",
    )}
