from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from configs.auth_dependencies import authenticated_context, csrf_context
from configs.database import get_db
from schemas.auth_schema import AuthContext
from schemas.flower_schema import FlowerCreate, FlowerUpdate, FlowerBOM, FlowerResponse, FlowerPage
from schemas.flower_schema import CatalogueCost, CatalogueListQuery
from use_cases.flowers.create_flower import create_flower
from use_cases.flowers.get_flower import get_flower
from use_cases.flowers.list_flowers import list_flowers
from use_cases.flowers.update_flower import update_flower
from use_cases.flowers.archive_flower import archive_flower
from use_cases.flowers.get_bom import get_bom
from use_cases.flowers.replace_bom import replace_bom
from use_cases.flowers.get_cost import get_cost

router = APIRouter(prefix="/flowers", tags=["flowers"])


@router.post("", response_model=FlowerResponse, status_code=201)
def create_endpoint(data: FlowerCreate, actor: AuthContext = Depends(csrf_context), db: Session = Depends(get_db)):
    return create_flower(db, actor, data)


@router.get("", response_model=FlowerPage)
def list_endpoint(filters: Annotated[CatalogueListQuery, Query()], actor: AuthContext = Depends(authenticated_context), db: Session = Depends(get_db)):
    return list_flowers(db, filters)


@router.get("/{entity_id}", response_model=FlowerResponse)
def get_endpoint(entity_id: UUID, actor: AuthContext = Depends(authenticated_context), db: Session = Depends(get_db)):
    return get_flower(db, entity_id)


@router.patch("/{entity_id}", response_model=FlowerResponse)
def update_endpoint(entity_id: UUID, data: FlowerUpdate, actor: AuthContext = Depends(csrf_context), db: Session = Depends(get_db)):
    return update_flower(db, actor, entity_id, data)


@router.delete("/{entity_id}", status_code=204)
def archive_endpoint(entity_id: UUID, actor: AuthContext = Depends(csrf_context), db: Session = Depends(get_db)):
    archive_flower(db, actor, entity_id)


@router.get("/{entity_id}/bom", response_model=FlowerBOM)
def get_bom_endpoint(entity_id: UUID, actor: AuthContext = Depends(authenticated_context), db: Session = Depends(get_db)):
    return get_bom(db, entity_id)


@router.put("/{entity_id}/bom", response_model=FlowerBOM)
def replace_bom_endpoint(entity_id: UUID, data: FlowerBOM, actor: AuthContext = Depends(csrf_context), db: Session = Depends(get_db)):
    return replace_bom(db, actor, entity_id, data)


@router.get("/{entity_id}/cost", response_model=CatalogueCost)
def cost_endpoint(entity_id: UUID, actor: AuthContext = Depends(authenticated_context), db: Session = Depends(get_db)):
    return get_cost(db, entity_id)

