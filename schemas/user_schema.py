from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, SecretStr

Username = Annotated[str, Field(min_length=3, max_length=32, pattern=r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")]


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: Username
    password: SecretStr


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: Username | None = None
    password: SecretStr | None = None
    current_password: SecretStr | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    is_superadmin: bool
    created_at: datetime
