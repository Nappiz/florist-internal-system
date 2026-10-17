from crud import expense_categories_crud as crud


def list_categories(db,actor,filters):
    rows,total=crud.page(db,filters,active_only=not actor.user.is_superadmin)
    return {'items':rows,'total':total,'limit':filters.limit,'offset':filters.offset}
