from collections import defaultdict
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException

from crud import flowers_crud, products_crud
from models.flower_model import Flower
from models.material_model import Material
from use_cases.common.validation import require_active


def normalize_materials(db, lines):
    quantities = defaultdict(Decimal)
    units = {}
    for line in sorted(lines, key=lambda line: str(line.material_id)):
        material = require_active(db, Material, line.material_id)
        if line.unit != material.base_unit:
            raise HTTPException(422, "Satuan komponen harus sama dengan satuan dasar material.")
        quantities[material.id] += line.quantity_required
        units[material.id] = line.unit
    if any(amount > Decimal("99999999999999.999999") for amount in quantities.values()):
        raise HTTPException(422, "Jumlah komponen melebihi batas kuantitas.")
    return [{"material_id": key, "quantity_required": amount, "unit": units[key]} for key, amount in sorted(quantities.items(), key=lambda item: str(item[0]))]


def normalize_flowers(db, lines, extra_materials=()):
    quantities = defaultdict(Decimal)
    for line in sorted(lines, key=lambda line: str(line.flower_id)):
        require_active(db, Flower, line.flower_id)
        quantities[line.flower_id] += line.quantity_required
    material_rows = list(extra_materials)
    for flower_id in sorted(quantities, key=str):
        rows = flowers_crud.materials(db, flower_id)
        if not rows:
            raise HTTPException(422, "Bunga aktif wajib memiliki komposisi material.")
        material_rows.extend(rows)
    _validate_material_rows(db, material_rows)
    if any(amount > Decimal("99999999999999.999999") for amount in quantities.values()):
        raise HTTPException(422, "Jumlah bunga melebihi batas kuantitas.")
    return [{"flower_id": key, "quantity_required": amount} for key, amount in sorted(quantities.items(), key=lambda item: str(item[0]))]


def validate_flower_recipe(db, flower_id, *, lock=True):
    rows = flowers_crud.materials(db, UUID(str(flower_id)))
    if not rows:
        raise HTTPException(422, "Bunga aktif wajib memiliki komposisi material.")
    _validate_material_rows(db, rows, lock=lock)


def _active_reference(db, model, identity, *, lock):
    if lock:
        return require_active(db, model, identity)
    row = db.get(model, identity)
    if row is None:
        raise HTTPException(404, "Referensi tidak ditemukan.")
    if not row.is_active:
        raise HTTPException(409, "Referensi sudah diarsipkan.")
    return row


def _validate_material_rows(db, rows, *, lock=True):
    for row in sorted(rows, key=lambda row: str(row.material_id)):
        material = _active_reference(db, Material, row.material_id, lock=lock)
        if row.unit != material.base_unit:
            raise HTTPException(422, "Satuan resep tidak sesuai satuan dasar material.")


def validate_product_recipe(db, product_id, *, lock=True):
    product_id = UUID(str(product_id))
    flowers = products_crud.flowers(db, product_id)
    materials = products_crud.materials(db, product_id)
    if not flowers and not materials:
        raise HTTPException(422, "Produk aktif wajib memiliki komposisi.")
    for row in flowers:
        _active_reference(db, Flower, row.flower_id, lock=lock)
    all_materials = list(materials)
    for row in flowers:
        rows = flowers_crud.materials(db, row.flower_id)
        if not rows:
            raise HTTPException(422, "Bunga aktif wajib memiliki komposisi material.")
        all_materials.extend(rows)
    _validate_material_rows(db, all_materials, lock=lock)


def mutation_values(data, *, exclude=None):
    values = data.model_dump(exclude_unset=True, exclude=exclude or set())
    for key in ("sku", "name", "selling_price", "estimated_labor_cost", "assembly_labor_cost", "is_active"):
        if key in values and values[key] is None:
            raise HTTPException(422, "Field wajib tidak boleh null.")
    if values.get("image_url") is not None:
        url = values["image_url"]
        if url.username is not None or url.password is not None or len(str(url)) > 2048:
            raise HTTPException(422, "URL gambar tidak valid.")
        values["image_url"] = str(url)
    return values

