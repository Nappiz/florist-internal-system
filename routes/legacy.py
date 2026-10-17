from fastapi import APIRouter,Depends,HTTPException
from configs.auth_dependencies import csrf_context
from routes.suppliers import router as suppliers_router
from routes.expenses import router as expenses_router

router=APIRouter(tags=['legacy archive'])
for previous in (suppliers_router,expenses_router):
    for route in previous.routes:
        if route.methods=={'GET'}:
            route.deprecated=True
            router.routes.append(route)


@router.api_route('/suppliers',methods=['POST'],include_in_schema=False)
@router.api_route('/suppliers/{identity}',methods=['PATCH','DELETE'],include_in_schema=False)
@router.api_route('/expenses',methods=['POST'],include_in_schema=False)
@router.api_route('/expenses/{identity}',methods=['PATCH','DELETE'],include_in_schema=False)
def retired_mutation(context=Depends(csrf_context)):
    raise HTTPException(410,'Endpoint lama hanya arsip. Gunakan katalog /api/v1/materials, /api/v1/suppliers, /api/v1/supplier-materials dan transaksi /api/v1/purchases.')
