"""
stored_files — ORM 對應 ops.stored_files（Application UC 上傳鏈路使用）。

檔名 `stored_files.py` → 類別 `StoredFiles`；資料表隸屬 **ops** schema，與 application.attachments.file_id 邏輯關聯。
"""

from __future__ import annotations

from sqlalchemy import BigInteger, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class StoredFiles(Base):
    """物件儲存之中繼資料（bucket／object_key／checksum）。"""

    __tablename__ = "stored_files"
    __table_args__ = {"schema": "ops"}

    file_id = Column(UUID(as_uuid=True), primary_key=True)
    bucket_name = Column(String(100), nullable=False)
    object_key = Column(String(255), nullable=False)
    storage_provider = Column(String(30), nullable=False)
    mime_type = Column(String(100), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    checksum_sha256 = Column(String(64), nullable=False)
    virus_scan_status = Column(String(30), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
