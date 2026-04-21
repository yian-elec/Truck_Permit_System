"""
permissions — ORM 對應 iam.permissions。
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class Permissions(Base):
    """權限定義主檔。"""

    __tablename__ = "permissions"
    __table_args__ = {"schema": "iam"}

    permission_code = Column(String(100), primary_key=True)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
