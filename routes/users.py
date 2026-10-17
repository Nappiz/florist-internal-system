from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from configs.auth_dependencies import administration_context, authenticated_context
from configs.database import get_db
from schemas.auth_schema import AuthContext
from schemas.user_schema import StatusInput, UserCreate, UserResponse, UserUpdate
from use_cases.users.create_user import create_user
from use_cases.users.delete_user import delete_user
from use_cases.users.get_user import get_user
from use_cases.users.list_users import list_users
from use_cases.users.update_user import update_user
from schemas.user_schema import UserListQuery,UserPage
from use_cases.users.list_user_page import list_user_page
from use_cases.users.update_status import update_status

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=201)
def create_user_endpoint(data: UserCreate, actor: AuthContext = Depends(administration_context), db: Session = Depends(get_db)):
    return create_user(db, actor, data)


@router.get("", response_model=list[UserResponse])
def list_users_endpoint(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0, le=1_000_000),
    actor: AuthContext = Depends(authenticated_context),
    db: Session = Depends(get_db),
):
    return list_users(db, actor, limit, offset)


@router.get("/{user_id}", response_model=UserResponse)
def get_user_endpoint(user_id: UUID, actor: AuthContext = Depends(authenticated_context), db: Session = Depends(get_db)):
    return get_user(db, actor, user_id)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user_endpoint(user_id: UUID, data: UserUpdate, request: Request, actor: AuthContext = Depends(administration_context), db: Session = Depends(get_db)):
    return update_user(db, actor, user_id, data, request.client.host if request.client else "unknown")


@router.delete("/{user_id}", status_code=204)
def delete_user_endpoint(user_id: UUID, actor: AuthContext = Depends(administration_context), db: Session = Depends(get_db)):
    delete_user(db, actor, user_id)


@router.patch("/{user_id}/status", response_model=UserResponse)
def status_endpoint(user_id: UUID, data: StatusInput, actor: AuthContext = Depends(administration_context), db: Session = Depends(get_db)):
    return update_status(db, actor, user_id, data)


# Existing unversioned frontend keeps its array; v1 consistently returns a page.
versioned_router=APIRouter(prefix='/users',tags=['users'])
for route in router.routes:
    if not (route.path=='/users' and route.methods=={'GET'}):
        versioned_router.routes.append(route)


@versioned_router.get('',response_model=UserPage)
def list_user_page_endpoint(query:Annotated[UserListQuery,Query()],actor:AuthContext=Depends(authenticated_context),db:Session=Depends(get_db)):
    return list_user_page(db,actor,query)
