"""NoopAuditLogPort — 不寫稽核（測試／預設）。"""

from __future__ import annotations

from src.contexts.iam.app.services.ports.audit_log_port import AuditLogPort, IamAuditRecord


class NoopAuditLogPort:
    def append(self, record: IamAuditRecord) -> None:
        _ = record
        return None
