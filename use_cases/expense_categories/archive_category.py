from schemas.expense_category_schema import CategoryUpdate
from use_cases.expense_categories.update_category import update_category


def archive_category(db,actor,category_id):
    return update_category(db,actor,category_id,CategoryUpdate(is_active=False))
