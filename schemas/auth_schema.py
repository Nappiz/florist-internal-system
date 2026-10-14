from dataclasses import dataclass, field
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, SecretStr

from models.auth_session_model import AuthSession
from models.user_model import User
from schemas.user_schema import UserResponse


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=1, max_length=32)
    password: SecretStr


class SessionResponse(BaseModel):
    user: UserResponse
    csrf_token: str
    expires_at: datetime


@dataclass(frozen=True)
class AuthContext:
    user: User
    session: AuthSession
    csrf_token: str = field(repr=False)


@dataclass(frozen=True)
class LoginResult:
    user: User
    expires_at: datetime
    token: str = field(repr=False)
    csrf_token: str = field(repr=False)
