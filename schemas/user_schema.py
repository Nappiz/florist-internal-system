from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, SecretStr, StringConstraints

Username = Annotated[str, Field(min_length=3, max_length=32, pattern=r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")]
FullName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
Email = Annotated[str, StringConstraints(strip_whitespace=True, to_lower=True, min_length=3, max_length=254, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")]
Role = Literal["staff", "superadmin"]


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: Username
    password: SecretStr
    full_name: FullName
    email: Email
    role: Role = "staff"


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: Username | None = None
    password: SecretStr | None = None
    current_password: SecretStr | None = None
    full_name: FullName | None = None
    email: Email | None = None
    role: Role | None = None
    is_active: bool | None = None


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: FullName | None = None
    email: Email | None = None


class PasswordUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    password: SecretStr
    current_password: SecretStr


class StatusInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_active: bool


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    full_name: str
    email: str
    role: Role
    is_active: bool
    is_superadmin: bool
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None
    created_by: UUID | None


class UserListQuery(BaseModel):
    model_config=ConfigDict(extra='forbid')
    q: str | None=Field(None,min_length=1,max_length=100)
    role: Role | None=None
    is_active: bool | None=None
    limit: int=Field(20,ge=1,le=100)
    offset: int=Field(0,ge=0,le=1_000_000)


class UserPage(BaseModel):
    items: list[UserResponse]
    total: int
    limit: int
    offset: int
