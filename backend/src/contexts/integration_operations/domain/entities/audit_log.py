"""
稽核紀錄聚合（Aggregate Root）。

責任：對應 ops.audit_logs 與 UC-OPS-03；稽核為附錄型寫入，建立後在領域中視為不可變，
以符合「關鍵交易完成後寫 audit、記錄 before／after」且不可竄改歷史的要求。

actor_user_id 可為空（系統或整合帳號）；client_ip 以字串形式持有，避免 Domain 依賴網路型別。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from ..value_objects import ActionCode, ActorType, AuditJsonSnapshot, ResourceId, ResourceType


@dataclass(frozen=True)
class AuditLog:
    """
    稽核紀錄（聚合根，不可變）。

    責任：封裝單次可稽核行為的完整欄位；不提供 mutator，避免領域層修改已持久化之稽核。
    """

    audit_log_id: UUID
    actor_user_id: UUID | None
    actor_type: ActorType
    action_code: ActionCode
    resource_type: ResourceType
    resource_id: ResourceId
    before_snapshot: AuditJsonSnapshot
    after_snapshot: AuditJsonSnapshot
    client_ip: str | None
    created_at: datetime

    @classmethod
    def record(
        cls,
        *,
        actor_user_id: UUID | None,
        actor_type: ActorType,
        action_code: ActionCode,
        resource_type: ResourceType,
        resource_id: ResourceId,
        before: dict[str, Any] | list[Any] | None,
        after: dict[str, Any] | list[Any] | None,
        created_at: datetime,
        client_ip: str | None = None,
        audit_log_id: UUID | None = None,
    ) -> AuditLog:
        """
        建立一筆稽核紀錄（對應關鍵交易完成後寫入）。

        before／after 以 AuditJsonSnapshot 包裝，允許 None 表示未提供快照。
        """
        ip = (client_ip or "").strip() or None
        return cls(
            audit_log_id=audit_log_id or uuid4(),
            actor_user_id=actor_user_id,
            actor_type=actor_type,
            action_code=action_code,
            resource_type=resource_type,
            resource_id=resource_id,
            before_snapshot=AuditJsonSnapshot(before),
            after_snapshot=AuditJsonSnapshot(after),
            client_ip=ip,
            created_at=created_at,
        )
