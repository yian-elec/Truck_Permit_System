"""
role_permissions — ORM 對應 iam.role_permissions。
"""

from __future__ import annotations

from sqlalchemy import Column, ForeignKey, String

from shared.core.db.connection import Base


class RolePermissions(Base):
    """角色—權限對照（複合主鍵）。"""

    __tablename__ = "role_permissions"
    __table_args__ = {"schema": "iam"}

    role_code = Column(
        String(50),
        ForeignKey("iam.roles.role_code", ondelete="CASCADE"),
        primary_key=True,
    )
    permission_code = Column(
        String(100),
        ForeignKey("iam.permissions.permission_code", ondelete="CASCADE"),
        primary_key=True,
    )
