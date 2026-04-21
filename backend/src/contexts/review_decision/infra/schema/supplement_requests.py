"""
supplement_requests — ORM 對應 review.supplement_requests。
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class SupplementRequests(Base):
    """補件請求主檔（對應領域 SupplementRequest 聚合）。"""

    __tablename__ = "supplement_requests"
    __table_args__ = {"schema": "review"}

    supplement_request_id = Column(UUID(as_uuid=True), primary_key=True)
    application_id = Column(UUID(as_uuid=True), nullable=False)
    requested_by = Column(UUID(as_uuid=True), nullable=False)
    deadline_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(30), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
