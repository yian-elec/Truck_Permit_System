"""
page_model_snapshots — ORM 對應 page_model.page_model_snapshots。

責任：持久化可選之 Page Model 快取列（聚合 read model 之 JSON 快照與契約版本），
供 Infra 寫入／讀取；業務組版規則仍屬 Domain／App。類別名依檔名 `page_model_snapshots` 轉為 `PageModelSnapshots`。
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class PageModelSnapshots(Base):
    """
    Page Model 快照列（快取或稽核用）。

    責任：以 `cache_key` 唯一識別一筆快取；`payload_json` 存放與前端契約一致之 JSON；
    `page_kind` 對應領域 `PageModelKind` 字串值。
    """

    __tablename__ = "page_model_snapshots"
    __table_args__ = {"schema": "page_model"}

    snapshot_id = Column(UUID(as_uuid=True), primary_key=True)
    page_kind = Column(String(64), nullable=False)
    application_id = Column(UUID(as_uuid=True), nullable=True)
    cache_key = Column(String(512), unique=True, nullable=False)
    payload_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    contract_version_major = Column(Integer, nullable=False, server_default="1")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
