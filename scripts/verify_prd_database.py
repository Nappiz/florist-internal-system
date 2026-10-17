"""Read-only schema and migration verification, without exporting business rows."""
from sqlalchemy import text
from configs.database import get_engine
from models import Base


def verify():
    names=sorted(Base.metadata.tables)
    with get_engine().connect() as connection:
        revision=connection.scalar(text('SELECT version_num FROM alembic_version'))
        rows=connection.execute(text("SELECT c.relname,c.relrowsecurity FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relname=ANY(:names)"),{'names':names}).all()
        if len(rows)!=len(names) or not all(row.relrowsecurity for row in rows): raise RuntimeError('Tabel aplikasi tidak lengkap atau RLS belum aktif.')
        for role in ('anon','authenticated','service_role'):
            exposed=connection.scalar(text("SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relname=ANY(:names) AND has_table_privilege(:role,c.oid,'SELECT,INSERT,UPDATE,DELETE')"),{'names':names,'role':role})
            if exposed: raise RuntimeError('Ada tabel aplikasi dengan grant API yang tidak diharapkan.')
        source=connection.scalar(text('SELECT count(*) FROM suppliers'))
        copied=connection.scalar(text('SELECT count(*) FROM suppliers s JOIN supplier_materials sm ON s.id=sm.id'))
        if source!=copied: raise RuntimeError('Copy listing legacy tidak lengkap.')
    print('Revision:',revision,'App tables:',len(names),'RLS: OK; API role grants: NONE; Legacy listing copy: OK')


if __name__=='__main__': verify()
