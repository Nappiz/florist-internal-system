from crud import operational_expenses_crud as crud
from use_cases.operational_expenses.access import validate_filters
from use_cases.operational_expenses.expense_response import expense_response


def list_expenses(db,actor,filters):
    validate_filters(filters)
    owner=None if actor.user.is_superadmin else actor.user.id
    return {'items':[expense_response(db,row) for row in crud.list_rows(db,filters,owner)],'total':crud.count(db,filters,owner),'page':filters.page,'page_size':filters.page_size}
