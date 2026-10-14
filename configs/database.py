from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import Session

from configs.settings import get_settings


def get_database_url() -> URL:
    value = get_settings().database_url
    if value is None or not value.get_secret_value().strip():
        raise ValueError("Isi DATABASE_URL PostgreSQL Supabase di backend/.env.")

    try:
        url = make_url(value.get_secret_value())
    except (ArgumentError, ValueError):
        raise ValueError("DATABASE_URL harus berupa connection string PostgreSQL valid.") from None

    if url.drivername not in {"postgres", "postgresql", "postgresql+psycopg"}:
        raise ValueError("DATABASE_URL harus berupa connection string PostgreSQL.")
    if not all((url.host, url.database, url.username, url.password)):
        raise ValueError("DATABASE_URL harus berisi host, database, username, dan password.")
    return url.set(drivername="postgresql+psycopg")


@lru_cache
def get_engine() -> Engine:
    return create_engine(
        get_database_url(),
        pool_pre_ping=True,
        hide_parameters=True,
        connect_args={"sslmode": "require", "connect_timeout": 10},
    )


def get_db() -> Iterator[Session]:
    with Session(get_engine()) as session:
        yield session
