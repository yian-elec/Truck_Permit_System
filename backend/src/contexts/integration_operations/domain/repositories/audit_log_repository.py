"""
AuditLog 儲存庫介面（Domain 埠）。

責任：稽核為僅附加寫入與查詢；介面不暗示可更新或刪除，以符合 UC-OPS-03。
"""

from abc import ABC, abstractmethod
from typing import Optional, Sequence
from uuid import UUID

from ..entities.audit_log import AuditLog


class AuditLogRepository(ABC):
    """
    稽核紀錄儲存庫介面。

    用途：附加寫入新 AuditLog；查詢供 review／admin（對應 GET audit-logs 的分頁／篩選由 App 組 query）。
    """

    @abstractmethod
    def append(self, log: AuditLog) -> None:
        """附加一筆不可變稽核紀錄。"""

    @abstractmethod
    def find_by_id(self, audit_log_id: UUID) -> Optional[AuditLog]:
        """依主鍵載入單筆稽核（選用，利於詳情或關聯除錯）。"""

    @abstractmethod
    def find_recent(
        self,
        *,
        limit: int,
        offset: int,
    ) -> Sequence[AuditLog]:
        """
        取得最近稽核紀錄（簽章僅表達領域可查詢性；實際排序／篩選由 Infra SQL 實作）。

        App 層可改以專用 query DTO 擴充此介面，不修改聚合。
        """
