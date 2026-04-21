"""
AuditLogRepository 實作 — 使用 get_session()。
"""

from __future__ import annotations

from typing import Optional, Sequence
from uuid import UUID

from shared.core.db.connection import get_session

from src.contexts.integration_operations.domain.entities import AuditLog
from src.contexts.integration_operations.domain.repositories import AuditLogRepository
from src.contexts.integration_operations.infra.repositories._mappers import (
    audit_log_from_row,
    audit_log_to_row,
)
from src.contexts.integration_operations.infra.schema import AuditLogs


class AuditLogRepositoryImpl(AuditLogRepository):
    """audit_logs 附加寫入與查詢。"""

    def append(self, log: AuditLog) -> None:
        row = audit_log_to_row(log)
        with get_session() as session:
            session.add(row)

    def find_by_id(self, audit_log_id: UUID) -> Optional[AuditLog]:
        with get_session() as session:
            row = session.query(AuditLogs).filter(AuditLogs.audit_log_id == audit_log_id).first()
            if row is None:
                return None
            return audit_log_from_row(row)

    def find_recent(self, *, limit: int, offset: int) -> Sequence[AuditLog]:
        with get_session() as session:
            rows = (
                session.query(AuditLogs)
                .order_by(AuditLogs.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
            return tuple(audit_log_from_row(r) for r in rows)
