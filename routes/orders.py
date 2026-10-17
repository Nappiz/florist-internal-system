from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.orm import Session

from configs.auth_dependencies import authenticated_context, csrf_context
from configs.database import get_db
from schemas.auth_schema import AuthContext
from schemas.order_schema import OrderAction, OrderCancel, OrderCreate, OrderListQuery, OrderPage, OrderPaymentCreate, OrderResponse, OrderUpdate
from use_cases.orders.add_payment import add_payment
from use_cases.orders.cancel_order import cancel_order
from use_cases.orders.complete_order import complete_order
from use_cases.orders.complete_production import complete_production
from use_cases.orders.confirm_order import confirm_order
from use_cases.orders.create_order import create_order
from use_cases.orders.get_order import get_order
from use_cases.orders.list_orders import list_orders
from use_cases.orders.start_production import start_production
from use_cases.orders.update_order import update_order

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=OrderPage)
def list_endpoint(filters: Annotated[OrderListQuery, Query()], actor: AuthContext = Depends(authenticated_context), db: Session = Depends(get_db)):
    return list_orders(db, filters)


@router.post("", response_model=OrderResponse, status_code=201)
def create_endpoint(data: OrderCreate, actor: AuthContext = Depends(csrf_context), db: Session = Depends(get_db)):
    return create_order(db, actor, data)


@router.get("/{order_id}", response_model=OrderResponse)
def get_endpoint(order_id: UUID, actor: AuthContext = Depends(authenticated_context), db: Session = Depends(get_db)):
    return get_order(db, order_id)


@router.patch("/{order_id}", response_model=OrderResponse)
def update_endpoint(order_id: UUID, data: OrderUpdate, actor: AuthContext = Depends(csrf_context), db: Session = Depends(get_db)):
    return update_order(db, actor, order_id, data)


@router.post("/{order_id}/confirm", response_model=OrderResponse)
def confirm_endpoint(order_id: UUID, data: OrderAction = Body(default=OrderAction()), actor: AuthContext = Depends(csrf_context), db: Session = Depends(get_db)):
    return confirm_order(db, actor, order_id)


@router.post("/{order_id}/start-production", response_model=OrderResponse)
def start_endpoint(order_id: UUID, data: OrderAction = Body(default=OrderAction()), actor: AuthContext = Depends(csrf_context), db: Session = Depends(get_db)):
    return start_production(db, actor, order_id)


@router.post("/{order_id}/complete-production", response_model=OrderResponse)
def production_endpoint(order_id: UUID, data: OrderAction = Body(default=OrderAction()), actor: AuthContext = Depends(csrf_context), db: Session = Depends(get_db)):
    return complete_production(db, actor, order_id)


@router.post("/{order_id}/complete", response_model=OrderResponse)
def complete_endpoint(order_id: UUID, data: OrderAction = Body(default=OrderAction()), actor: AuthContext = Depends(csrf_context), db: Session = Depends(get_db)):
    return complete_order(db, actor, order_id)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_endpoint(order_id: UUID, data: OrderCancel = Body(default=OrderCancel()), actor: AuthContext = Depends(csrf_context), db: Session = Depends(get_db)):
    return cancel_order(db, actor, order_id, data)


@router.post("/{order_id}/payments", response_model=OrderResponse)
def payment_endpoint(order_id: UUID, data: OrderPaymentCreate, actor: AuthContext = Depends(csrf_context), db: Session = Depends(get_db)):
    return add_payment(db, actor, order_id, data)
