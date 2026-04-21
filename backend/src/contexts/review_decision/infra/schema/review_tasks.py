"""
review_tasks — ORM 對應 review.review_tasks。
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class ReviewTasks(Base):
    """審查任務主檔（對應領域 ReviewTask 聚合持久化列）。"""

    __tablename__ = "review_tasks"
    __table_args__ = {"schema": "review"}

    review_task_id = Column(UUID(as_uuid=True), primary_key=True)
    application_id = Column(UUID(as_uuid=True), nullable=False)
    stage = Column(String(30), nullable=False)
    status = Column(String(30), nullable=False)
    assignee_user_id = Column(UUID(as_uuid=True), nullable=True)
    due_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
