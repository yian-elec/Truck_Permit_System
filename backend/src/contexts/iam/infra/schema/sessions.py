"""
sessions — ORM 對應 iam.sessions。
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import INET, UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class Sessions(Base):
    """登入工作階段與 token JTI。"""

    __tablename__ = "sessions"
    __table_args__ = {"schema": "iam"}

    session_id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("iam.users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    access_token_jti = Column(String(100), unique=True, nullable=False)
    refresh_token_jti = Column(String(100), unique=True, nullable=True)
    client_ip = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    issued_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
