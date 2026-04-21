"""
applications — ORM 對應 application.applications。
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class Applications(Base):
    """申請案件主表（Aggregate 主列）。"""

    __tablename__ = "applications"
    __table_args__ = {"schema": "application"}

    application_id = Column(UUID(as_uuid=True), primary_key=True)
    application_no = Column(String(30), unique=True, nullable=False)
    applicant_user_id = Column(UUID(as_uuid=True), nullable=True)
    status = Column(String(30), nullable=False)
    applicant_type = Column(String(30), nullable=False)
    reason_type = Column(String(50), nullable=False)
    reason_detail = Column(Text, nullable=True)
    requested_start_at = Column(DateTime(timezone=True), nullable=False)
    requested_end_at = Column(DateTime(timezone=True), nullable=False)
    delivery_method = Column(String(30), nullable=False)
    source_channel = Column(String(30), nullable=False)
    consent_accepted_at = Column(DateTime(timezone=True), nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    version = Column(Integer, nullable=False, server_default="1")
