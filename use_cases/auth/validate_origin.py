from fastapi import HTTPException

from configs.settings import get_settings


def validate_origin(origin: str | None) -> None:
    if origin is None or origin not in get_settings().allowed_origins:
        raise HTTPException(403, "Request origin tidak diizinkan.")
