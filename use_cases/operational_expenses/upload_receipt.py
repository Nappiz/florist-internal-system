from uuid import uuid4
from fastapi import HTTPException
from models.expense_receipt_model import ExpenseReceipt
from use_cases.operational_expenses.access import get_authorized,require_draft
from use_cases.common.persistence import finish,flush
from use_cases.audit.record import record
from services.expense_receipt_storage import save_receipt,remove_receipt

MAX_RECEIPT_BYTES=5*1024*1024


async def upload_receipt(db,actor,expense_id,chunks,content_type):
    row=get_authorized(db,actor,expense_id,lock=True)
    if not actor.user.is_superadmin: require_draft(row)
    if row.status=='void': raise HTTPException(409,'Expense void tidak dapat menerima lampiran.')
    mime=(content_type or '').split(';',1)[0].strip().lower()
    signatures={'image/jpeg':(b'\xff\xd8\xff','jpg'),'image/png':(b'\x89PNG\r\n\x1a\n','png'),'application/pdf':(b'%PDF-','pdf')}
    if mime not in signatures: raise HTTPException(415,'Hanya JPG, PNG, dan PDF yang diperbolehkan.')
    content=bytearray()
    async for chunk in chunks:
        if len(content)+len(chunk)>MAX_RECEIPT_BYTES: raise HTTPException(413,'Ukuran receipt maksimal 5 MB.')
        content.extend(chunk)
    signature,extension=signatures[mime]
    if not content.startswith(signature): raise HTTPException(415,'Isi file tidak sesuai tipe konten.')
    name=str(uuid4())
    save_receipt(name,content)
    try:
        receipt=ExpenseReceipt(expense_id=row.id,storage_name=name,mime_type=mime,size_bytes=len(content),original_name='receipt.'+extension,created_by=actor.user.id)
        db.add(receipt); flush(db)
        record(db,actor,'upload_receipt','operating_expense',row.id,{'receipt_id':str(receipt.id)})
        finish(db)
    except Exception:
        db.rollback(); remove_receipt(name); raise
    return {key:getattr(receipt,key) for key in ('id','expense_id','mime_type','size_bytes','original_name','created_at')}
