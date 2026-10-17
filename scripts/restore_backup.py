"""Restore a backend backup into a NEW isolated recovery schema for verification.

Never replaces public tables. Promote a verified restore using the deployment runbook.
"""
import argparse
import json
import re
from datetime import date,datetime
from decimal import Decimal
from pathlib import Path
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.schema import CreateSchema
from configs.database import get_engine
from models import Base


def restore(path:Path,schema:str):
    if re.fullmatch(r'recovery_[a-z0-9_]{1,40}',schema) is None:
        raise ValueError('Target harus schema baru dengan nama recovery_ diikuti huruf kecil/angka/underscore.')
    payload=json.loads(path.read_text(encoding='utf-8'))
    if payload.get('format_version')!=1 or not isinstance(payload.get('tables'),dict): raise ValueError('Format backup tidak didukung.')
    if set(payload['tables'])!=set(Base.metadata.tables): raise ValueError('Gunakan kode/model yang cocok dengan revision backup sebelum restore; daftar tabel berbeda.')
    engine=get_engine()
    with engine.begin() as connection:
        connection.execute(CreateSchema(schema))
        target=connection.execution_options(schema_translate_map={None:schema})
        Base.metadata.create_all(target)
        user_creators=[]
        for table in Base.metadata.sorted_tables:
            rows=payload['tables'].get(table.name,[])
            converted=[]
            for row in rows:
                values={}
                for key,value in row.items():
                    column=table.c[key]
                    if value is not None:
                        if isinstance(column.type,sa.Uuid): value=UUID(value)
                        elif isinstance(column.type,sa.DateTime): value=datetime.fromisoformat(value)
                        elif isinstance(column.type,sa.Date): value=date.fromisoformat(value)
                        elif isinstance(column.type,sa.Numeric): value=Decimal(value)
                    values[key]=value
                converted.append(values)
                if table.name=='users' and values.get('created_by') is not None:
                    user_creators.append((values['id'],values['created_by']))
                    values['created_by']=None
            if converted: target.execute(table.insert(),converted)
            if table.name=='users':
                for identity,creator in user_creators:
                    target.execute(table.update().where(table.c.id==identity).values(created_by=creator))
        # Supabase API roles must not acquire access to private recovery data.
        for table in Base.metadata.sorted_tables:
            target.exec_driver_sql(f'ALTER TABLE "{schema}"."{table.name}" ENABLE ROW LEVEL SECURITY')
            target.exec_driver_sql(f'REVOKE ALL ON TABLE "{schema}"."{table.name}" FROM PUBLIC, anon, authenticated, service_role')
        target.exec_driver_sql(f'REVOKE ALL ON SCHEMA "{schema}" FROM PUBLIC, anon, authenticated, service_role')
    return {name:len(rows) for name,rows in payload['tables'].items()}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('backup',type=Path)
    parser.add_argument('--schema',required=True)
    args=parser.parse_args()
    counts=restore(args.backup,args.schema)
    print('Recovery schema:',args.schema,'Restored counts:',counts)
