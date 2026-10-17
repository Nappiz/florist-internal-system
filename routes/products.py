from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from configs.auth_dependencies import authenticated_context, csrf_context
from configs.database import get_db
from schemas.auth_schema import AuthContext
from schemas.product_schema import ProductCreate, ProductUpdate, ProductBOM, ProductResponse, ProductPage
from schemas.flower_schema import CatalogueCost, CatalogueListQuery
from use_cases.products.create_product import create_product
from use_cases.products.get_product import get_product
from use_cases.products.list_products import list_products
from use_cases.products.update_product import update_product
from use_cases.products.archive_product import archive_product
from use_cases.products.get_bom import get_bom
from use_cases.products.replace_bom import replace_bom
from use_cases.products.get_cost import get_cost

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=ProductResponse, status_code=201)
def create_endpoint(data: ProductCreate, actor: AuthContext = Depends(csrf_context), db: Session = Depends(get_db)):
    return create_product(db, actor, data)


@router.get("", response_model=ProductPage)
def list_endpoint(filters: Annotated[CatalogueListQuery, Query()], actor: AuthContext = Depends(authenticated_context), db: Session = Depends(get_db)):
    return list_products(db, filters)


@router.get("/{entity_id}", response_model=ProductResponse)
def get_endpoint(entity_id: UUID, actor: AuthContext = Depends(authenticated_context), db: Session = Depends(get_db)):
    return get_product(db, entity_id)


@router.patch("/{entity_id}", response_model=ProductResponse)
def update_endpoint(entity_id: UUID, data: ProductUpdate, actor: AuthContext = Depends(csrf_context), db: Session = Depends(get_db)):
    return update_product(db, actor, entity_id, data)


@router.delete("/{entity_id}", status_code=204)
def archive_endpoint(entity_id: UUID, actor: AuthContext = Depends(csrf_context), db: Session = Depends(get_db)):
    archive_product(db, actor, entity_id)


@router.get("/{entity_id}/bom", response_model=ProductBOM)
def get_bom_endpoint(entity_id: UUID, actor: AuthContext = Depends(authenticated_context), db: Session = Depends(get_db)):
    return get_bom(db, entity_id)


@router.put("/{entity_id}/bom", response_model=ProductBOM)
def replace_bom_endpoint(entity_id: UUID, data: ProductBOM, actor: AuthContext = Depends(csrf_context), db: Session = Depends(get_db)):
    return replace_bom(db, actor, entity_id, data)


@router.get("/{entity_id}/cost", response_model=CatalogueCost)
def cost_endpoint(entity_id: UUID, actor: AuthContext = Depends(authenticated_context), db: Session = Depends(get_db)):
    return get_cost(db, entity_id)

