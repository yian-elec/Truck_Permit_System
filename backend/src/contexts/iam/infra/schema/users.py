"""
users — ORM 對應 iam.users。
"""

from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class Users(Base):
    """使用者主表（與既有 public users 分離；UUID 主鍵）。"""

    __tablename__ = "users"
    __table_args__ = {"schema": "iam"}

    user_id = Column(UUID(as_uuid=True), primary_key=True)
    account_type = Column(String(30), nullable=False)
    status = Column(String(30), nullable=False)
    username = Column(String(100), nullable=True, unique=True)
    password_hash = Column(String(255), nullable=True)
    display_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True)
    mobile = Column(String(30), nullable=True)
    external_provider = Column(String(50), nullable=True)
    external_subject = Column(String(255), nullable=True)
    mfa_enabled = Column(Boolean, nullable=False, server_default="false")
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)
