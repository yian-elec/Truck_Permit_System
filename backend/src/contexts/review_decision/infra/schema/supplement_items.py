"""
supplement_items — ORM 對應 review.supplement_items。
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class SupplementItems(Base):
    """補件請求細項（隸屬 supplement_requests）。"""

    __tablename__ = "supplement_items"
    __table_args__ = {"schema": "review"}

    supplement_item_id = Column(UUID(as_uuid=True), primary_key=True)
    supplement_request_id = Column(
        UUID(as_uuid=True),
        ForeignKey("review.supplement_requests.supplement_request_id"),
        nullable=False,
    )
    item_code = Column(String(50), nullable=False)
    item_name = Column(String(100), nullable=False)
    required_action = Column(String(30), nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
