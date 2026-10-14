from alembic import context
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from configs.database import get_database_url
from models import Base

target_metadata = Base.metadata


def include_object(object_, name, type_, reflected, compare_to):
    # Existing tables outside our models belong to Supabase or another application.
    return not (type_ == "table" and reflected and compare_to is None)


def run_migrations_offline() -> None:
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(
        get_database_url(),
        poolclass=NullPool,
        hide_parameters=True,
        connect_args={"sslmode": "require", "connect_timeout": 10},
    )
    try:
        with engine.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                include_object=include_object,
            )
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
