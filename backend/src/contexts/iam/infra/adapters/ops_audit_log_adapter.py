"""
ops_audit_log_adapter — 將 IAM 稽核紀錄轉寫至 `ops.audit_logs`（經 AuditApplicationService）。

啟用：環境變數 `IAM_APPEND_OPS_AUDIT=1` 並確保 `ops` schema 已初始化。
"""

from __future__ import annotations

from src.contexts.integration_operations.app.dtos.audit_dtos import RecordAuditLogInputDTO
from src.contexts.integration_operations.app.services.audit_application_service import (
    AuditApplicationService,
)
from src.contexts.integration_operations.infra.repositories.audit_log_repository_impl import (
    AuditLogRepositoryImpl,
)

from src.contexts.iam.app.services.ports.audit_log_port import AuditLogPort, IamAuditRecord


class OpsAuditLogAdapter(AuditLogPort):
    """IAM → integration_operations 稽核用例。"""

    def __init__(self, audit_service: AuditApplicationService | None = None) -> None:
        self._audit = audit_service or AuditApplicationService(AuditLogRepositoryImpl())

    def append(self, record: IamAuditRecord) -> None:
        self._audit.record(
            RecordAuditLogInputDTO(
                actor_user_id=record.actor_user_id,
                actor_type=record.actor_type,
                action_code=record.action_code,
                resource_type=record.resource_type,
                resource_id=record.resource_id,
                before_snapshot=record.before_snapshot,
                after_snapshot=record.after_snapshot,
                client_ip=record.client_ip,
            )
        )
