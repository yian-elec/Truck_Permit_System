"""
decisions — ORM 對應 review.decisions。
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class Decisions(Base):
    """審查決策紀錄（對應領域 ReviewDecision 單筆持久化列）。"""

    __tablename__ = "decisions"
    __table_args__ = {"schema": "review"}

    decision_id = Column(UUID(as_uuid=True), primary_key=True)
    application_id = Column(UUID(as_uuid=True), nullable=False)
    decision_type = Column(String(30), nullable=False)
    selected_candidate_id = Column(UUID(as_uuid=True), nullable=True)
    override_id = Column(UUID(as_uuid=True), nullable=True)
    approved_start_at = Column(DateTime(timezone=True), nullable=True)
    approved_end_at = Column(DateTime(timezone=True), nullable=True)
    reason = Column(Text, nullable=False)
    decided_by = Column(UUID(as_uuid=True), nullable=False)
    decided_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
