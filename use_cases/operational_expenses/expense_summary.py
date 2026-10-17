from crud import operational_expenses_crud as crud,expense_categories_crud
from use_cases.operational_expenses.access import require_superadmin,validate_filters


def expense_summary(db,actor,filters):
    require_superadmin(actor); validate_filters(filters)
    rows=[row for row in crud.list_rows(db,filters,paginate=False) if row.status=='posted']
    categories={row.id:row for row in expense_categories_crud.list_rows(db)}
    category_totals={}; trend={}; total=paid=0
    for row in rows:
        payment=crud.paid_amount(db,row.id)
        total+=row.amount; paid+=payment
        category=categories[row.category_id]
        group=category_totals.setdefault(str(category.id),{'category_id':category.id,'name':category.name,'classification':category.classification,'amount':0,'paid_amount':0})
        group['amount']+=row.amount; group['paid_amount']+=payment
        month=row.expense_date.strftime('%Y-%m')
        trend[month]=trend.get(month,0)+row.amount
    return {'date_basis':'expense_date','payment_basis':'non_reversed_payments_for_selected_expenses','total_posted_expenses':total,'total_paid_expenses':paid,'total_unpaid_expenses':total-paid,'by_category':list(category_totals.values()),'trend':[{'month':key,'amount':trend[key]} for key in sorted(trend)]}
