"""
certificate_access_logs — ORM 對應 permit.certificate_access_logs（UC-PERMIT-04）。
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import INET, UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class CertificateAccessLogs(Base):
    """使用證下載／存取紀錄。"""

    __tablename__ = "certificate_access_logs"
    __table_args__ = {"schema": "permit"}

    access_log_id = Column(UUID(as_uuid=True), primary_key=True)
    document_id = Column(UUID(as_uuid=True), nullable=False)
    permit_id = Column(UUID(as_uuid=True), nullable=False)
    accessed_by = Column(UUID(as_uuid=True), nullable=True)
    access_type = Column(String(30), nullable=False)
    client_ip = Column(INET, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
