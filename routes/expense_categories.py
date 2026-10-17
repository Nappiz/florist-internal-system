from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from configs.auth_dependencies import authenticated_context,csrf_context
from configs.database import get_db
from schemas.auth_schema import AuthContext
from schemas.expense_category_schema import CategoryCreate,CategoryUpdate,CategoryResponse
from schemas.catalogue_types import PageQuery,PageResponse
from use_cases.expense_categories.create_category import create_category
from use_cases.expense_categories.update_category import update_category
from use_cases.expense_categories.archive_category import archive_category
from use_cases.expense_categories.list_categories import list_categories

router=APIRouter(prefix='/expense-categories',tags=['expense-categories'])


@router.get('',response_model=PageResponse[CategoryResponse])
def list_endpoint(filters:Annotated[PageQuery,Query()],actor:AuthContext=Depends(authenticated_context),db:Session=Depends(get_db)):
    return list_categories(db,actor,filters)


@router.post('',response_model=CategoryResponse,status_code=201)
def create_endpoint(data:CategoryCreate,actor:AuthContext=Depends(csrf_context),db:Session=Depends(get_db)):
    return create_category(db,actor,data)


@router.patch('/{category_id}',response_model=CategoryResponse)
def update_endpoint(category_id:UUID,data:CategoryUpdate,actor:AuthContext=Depends(csrf_context),db:Session=Depends(get_db)):
    return update_category(db,actor,category_id,data)


@router.delete('/{category_id}',response_model=CategoryResponse)
def archive_endpoint(category_id:UUID,actor:AuthContext=Depends(csrf_context),db:Session=Depends(get_db)):
    return archive_category(db,actor,category_id)
