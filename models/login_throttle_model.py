from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class LoginThrottle(Base):
    __tablename__ = "login_throttles"
    __table_args__ = (CheckConstraint("attempts >= 1", name="ck_login_throttles_attempts"),)

    bucket_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False)
    window_started: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
