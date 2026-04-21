"""
documents — ORM 對應 permit.documents。
"""

from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class Documents(Base):
    """許可相關文件版本列（對應領域 PermitDocument／§8 permit.certificates）。"""

    __tablename__ = "documents"
    __table_args__ = {"schema": "permit"}

    document_id = Column(UUID(as_uuid=True), primary_key=True)
    permit_id = Column(UUID(as_uuid=True), nullable=True)
    application_id = Column(UUID(as_uuid=True), nullable=False)
    document_type = Column(String(50), nullable=False)
    file_id = Column(UUID(as_uuid=True), nullable=False)
    template_code = Column(String(50), nullable=False)
    version_no = Column(Integer, nullable=False)
    status = Column(String(30), nullable=False)
    is_latest = Column(Boolean, nullable=False, default=True)
    checksum_sha256 = Column(String(64), nullable=True)
    generated_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
