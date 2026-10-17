from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from models.expense_model import Expense
from schemas.expense_schema import ExpenseListQuery


def filtered_query(filters: ExpenseListQuery):
    query = select(Expense)
    if filters.q is not None:
        query = query.where(or_(
            Expense.material_name.icontains(filters.q, autoescape=True),
            Expense.store_name.icontains(filters.q, autoescape=True),
            Expense.variant.icontains(filters.q, autoescape=True),
            Expense.reference_number.icontains(filters.q, autoescape=True),
        ))
    if filters.supplier_id is not None:
        query = query.where(Expense.supplier_id == filters.supplier_id)
    if filters.date_from is not None:
        query = query.where(Expense.purchase_date >= filters.date_from)
    if filters.date_to is not None:
        query = query.where(Expense.purchase_date <= filters.date_to)
    if filters.min_total is not None:
        query = query.where(Expense.total_amount >= filters.min_total)
    if filters.max_total is not None:
        query = query.where(Expense.total_amount <= filters.max_total)
    return query


def count(db: Session, filters: ExpenseListQuery) -> int:
    return db.scalar(select(func.count()).select_from(filtered_query(filters).subquery()))


def list_expenses(db: Session, filters: ExpenseListQuery, order_by) -> list[Expense]:
    return list(db.scalars(filtered_query(filters)
        .order_by(order_by, Expense.purchase_date.desc(), Expense.created_at.desc(), Expense.id)
        .limit(filters.limit).offset(filters.offset)))


def get_by_id(db: Session, expense_id: UUID) -> Expense | None:
    return db.scalar(select(Expense).where(Expense.id == expense_id).with_for_update())


def add(db: Session, expense: Expense) -> Expense:
    db.add(expense)
    db.flush()
    return expense


def update(db: Session, expense: Expense, values: dict) -> None:
    for field, value in values.items():
        setattr(expense, field, value)
    db.flush()


def delete(db: Session, expense: Expense) -> None:
    db.delete(expense)
    db.flush()
