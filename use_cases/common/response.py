from decimal import Decimal
from sqlalchemy import inspect


def row_response(row):
    result={column.key:getattr(row,column.key) for column in inspect(row).mapper.column_attrs}
    return {key:str(value) if isinstance(value,Decimal) else value for key,value in result.items()}


def input_values(data,exclude_unset=False):
    values=data.model_dump(mode='python',exclude_unset=exclude_unset)
    return {key:str(value) if hasattr(value,'unicode_string') else value for key,value in values.items()}
