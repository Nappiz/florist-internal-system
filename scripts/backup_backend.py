"""Private logical backup of app-owned pre-PRD tables. Never prints row data."""
import json
from datetime import UTC,datetime
from pathlib import Path
from sqlalchemy import MetaData,Table,inspect,select,text
from configs.database import get_engine
from models import Base


def backup():
    folder=Path(__file__).resolve().parents[1]/'.backups'
    folder.mkdir(exist_ok=True)
    with get_engine().connect().execution_options(isolation_level='REPEATABLE READ') as connection:
        existing=set(inspect(connection).get_table_names())
        names=[table.name for table in Base.metadata.sorted_tables if table.name in existing]
        metadata=MetaData()
        tables={name:Table(name,metadata,autoload_with=connection) for name in names}
        revision=connection.scalar(text('SELECT version_num FROM alembic_version'))
        payload={'format_version':1,'created_at':datetime.now(UTC).isoformat(),'revision':revision,'tables':{name:[dict(row) for row in connection.execute(select(table)).mappings()] for name,table in tables.items()}}
    target=folder/f'backend_{datetime.now(UTC):%Y%m%dT%H%M%SZ}.json'
    target.write_text(json.dumps(payload,default=str,ensure_ascii=False),encoding='utf-8')
    print('Backup tersimpan di .backups/'+target.name)
    print('Revision:',revision,'Row counts:',{name:len(rows) for name,rows in payload['tables'].items()})
    return target


if __name__=='__main__':
    backup()
