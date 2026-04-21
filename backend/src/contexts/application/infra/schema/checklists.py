"""
checklists — ORM 對應 application.checklists。
"""

from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class Checklists(Base):
    """送件／補件檢核項目。"""

    __tablename__ = "checklists"
    __table_args__ = {"schema": "application"}

    checklist_id = Column(UUID(as_uuid=True), primary_key=True)
    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("application.applications.application_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_code = Column(String(50), nullable=False)
    item_name = Column(String(100), nullable=False)
    is_required = Column(Boolean, nullable=False)
    is_satisfied = Column(Boolean, nullable=False)
    source = Column(String(30), nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
