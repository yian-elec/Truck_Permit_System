"""
audit_log_port — UC-IAM-04 等寫入結構化稽核之出站埠。

實作可接 `integration_operations` 之 AuditApplicationService，預設 Noop。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Protocol
from uuid import UUID


@dataclass(frozen=True)
class IamAuditRecord:
    """IAM 用例寫入稽核之最小欄位（對應 RecordAuditLogInputDTO 子集）。"""

    actor_user_id: Optional[UUID]
    actor_type: str
    action_code: str
    resource_type: str
    resource_id: str
    before_snapshot: Optional[dict[str, Any] | list[Any]] = None
    after_snapshot: Optional[dict[str, Any] | list[Any]] = None
    client_ip: Optional[str] = None


class AuditLogPort(Protocol):
    def append(self, record: IamAuditRecord) -> None:
        """寫入一筆稽核；失敗時實作可選擇吞掉並打 log 或向外拋出。"""
        ...
