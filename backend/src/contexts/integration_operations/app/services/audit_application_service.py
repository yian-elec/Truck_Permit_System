"""
UC-OPS-03 — 稽核用例服務。

責任：將關鍵交易之 before／after 轉為 Domain AuditLog 並經 Repository 附加寫入。
"""

from __future__ import annotations

from datetime import datetime, timezone

from shared.core.logger.logger import logger

from src.contexts.integration_operations.app.dtos import RecordAuditLogInputDTO, RecordAuditLogOutputDTO
from src.contexts.integration_operations.domain.entities import AuditLog
from src.contexts.integration_operations.domain.errors import InvalidDomainValueError
from src.contexts.integration_operations.domain.repositories import AuditLogRepository
from src.contexts.integration_operations.domain.value_objects import ActionCode, ActorType, ResourceId, ResourceType


class AuditApplicationService:
    """稽核附加寫入；不提供更新／刪除。"""

    def __init__(self, audit_log_repository: AuditLogRepository) -> None:
        self._repo = audit_log_repository

    def record(self, dto: RecordAuditLogInputDTO) -> RecordAuditLogOutputDTO:
        """
        寫入一筆稽核紀錄。

        流程：DTO → VO／Domain.record → Repository.append。
        """
        now = datetime.now(timezone.utc)
        logger.info(
            "AuditApplicationService.record "
            f"action={dto.action_code} resource={dto.resource_type}/{dto.resource_id}"
        )
        try:
            log = AuditLog.record(
                actor_user_id=dto.actor_user_id,
                actor_type=ActorType(dto.actor_type),
                action_code=ActionCode(dto.action_code),
                resource_type=ResourceType(dto.resource_type),
                resource_id=ResourceId(dto.resource_id),
                before=dto.before_snapshot,
                after=dto.after_snapshot,
                created_at=now,
                client_ip=dto.client_ip,
            )
        except InvalidDomainValueError as e:
            logger.warn(f"audit validation failed: {e}")
            raise

        self._repo.append(log)
        return RecordAuditLogOutputDTO(audit_log_id=log.audit_log_id, created_at=log.created_at)
