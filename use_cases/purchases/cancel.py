from fastapi import HTTPException
from use_cases.common.persistence import finish
from use_cases.audit.record import record
from use_cases.purchases.response import require,response


def cancel(db,actor,identity):
    purchase=require(db,identity)
    if purchase.status not in {'draft','ordered'}: raise HTTPException(409,'Pembelian tidak dapat dibatalkan pada status ini.')
    purchase.status='cancelled'
    purchase.updated_by=actor.user.id
    record(db,actor,'cancel','purchase',identity)
    finish(db)
    return response(db,purchase)
