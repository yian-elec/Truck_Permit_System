"""
document_jobs — ORM 對應 permit.document_jobs。
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class DocumentJobs(Base):
    """文件產製工作單（對應領域 DocumentGenerationJob／§8 certificate_jobs）。"""

    __tablename__ = "document_jobs"
    __table_args__ = {"schema": "permit"}

    job_id = Column(UUID(as_uuid=True), primary_key=True)
    application_id = Column(UUID(as_uuid=True), nullable=False)
    permit_id = Column(UUID(as_uuid=True), nullable=True)
    job_type = Column(String(50), nullable=False)
    status = Column(String(30), nullable=False)
    error_message = Column(Text, nullable=True)
    triggered_by = Column(UUID(as_uuid=True), nullable=True)
    trigger_source = Column(String(30), nullable=False, server_default="system")
    retry_count = Column(Integer, nullable=False, server_default="0")
    payload_json = Column(JSONB, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
