"""
attachments — ORM 對應 application.attachments。

說明：file_id 與 ops.stored_files 邏輯關聯；未加 DB 層 ForeignKey，避免 seed 載入順序與跨 schema 循環依賴。
"""

from __future__ import annotations

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class Attachments(Base):
    """申請附件中繼資料（實體檔於 object storage／stored_files）。"""

    __tablename__ = "attachments"
    __table_args__ = {"schema": "application"}

    attachment_id = Column(UUID(as_uuid=True), primary_key=True)
    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("application.applications.application_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    attachment_type = Column(String(50), nullable=False)
    file_id = Column(UUID(as_uuid=True), nullable=False)
    original_filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    checksum_sha256 = Column(String(64), nullable=False)
    status = Column(String(30), nullable=False)
    ocr_status = Column(String(30), nullable=False, server_default="pending")
    uploaded_by = Column(UUID(as_uuid=True), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
