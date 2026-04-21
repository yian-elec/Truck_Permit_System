"""
review_comments — ORM 對應 review.review_comments。
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class ReviewComments(Base):
    """審查評論（對應領域 ReviewComment 寫入後之持久化列）。"""

    __tablename__ = "review_comments"
    __table_args__ = {"schema": "review"}

    comment_id = Column(UUID(as_uuid=True), primary_key=True)
    application_id = Column(UUID(as_uuid=True), nullable=False)
    comment_type = Column(String(30), nullable=False)
    content = Column(Text, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
