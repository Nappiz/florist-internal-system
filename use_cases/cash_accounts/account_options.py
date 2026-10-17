from crud import cash_accounts_crud


def account_options(db, actor, query):
    rows, total = cash_accounts_crud.page(db, query.model_copy(update={'is_active': True}))
    return {'items': [{'id': row.id, 'name': row.name, 'account_type': row.account_type} for row in rows], 'total': total, 'limit': query.limit, 'offset': query.offset}
