"""
roles — ORM 對應 iam.roles。
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class Roles(Base):
    """角色主檔（role_code 為業務鍵）。"""

    __tablename__ = "roles"
    __table_args__ = {"schema": "iam"}

    role_code = Column(String(50), primary_key=True)
    role_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
