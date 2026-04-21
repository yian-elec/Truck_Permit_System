"""
status_histories — ORM 對應 application.status_histories。
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class StatusHistories(Base):
    """案件狀態變更歷程（僅追加）。"""

    __tablename__ = "status_histories"
    __table_args__ = {"schema": "application"}

    history_id = Column(UUID(as_uuid=True), primary_key=True)
    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("application.applications.application_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    from_status = Column(String(30), nullable=True)
    to_status = Column(String(30), nullable=False)
    changed_by = Column(UUID(as_uuid=True), nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
