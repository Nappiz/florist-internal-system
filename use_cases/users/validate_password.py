import string

from fastapi import HTTPException


def validate_password(password: str) -> None:
    if not (
        8 <= len(password) <= 128
        and any(char.isupper() for char in password)
        and any(char.islower() for char in password)
        and any(char in string.punctuation for char in password)
    ):
        raise HTTPException(
            422,
            "Password harus 8–128 karakter, memiliki huruf besar, huruf kecil, dan karakter spesial.",
        )
