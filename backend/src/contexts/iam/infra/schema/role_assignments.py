"""
role_assignments — ORM 對應 iam.role_assignments。
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class RoleAssignments(Base):
    """使用者角色指派（可帶 scope）。"""

    __tablename__ = "role_assignments"
    __table_args__ = {"schema": "iam"}

    assignment_id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("iam.users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    role_code = Column(
        String(50),
        ForeignKey("iam.roles.role_code", ondelete="RESTRICT"),
        nullable=False,
    )
    scope_type = Column(String(50), nullable=True)
    scope_id = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
