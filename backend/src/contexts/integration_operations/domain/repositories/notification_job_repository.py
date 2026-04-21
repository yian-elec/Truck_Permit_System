"""
NotificationJob 儲存庫介面（Domain 埠）。

責任：定義通知作業聚合的持久化契約；實作在 Infra（例如對應 ops.notification_jobs）。
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from ..entities.notification_job import NotificationJob


class NotificationJobRepository(ABC):
    """
    通知作業儲存庫介面。

    用途：支援 UC-OPS-02 建立 job 與更新狀態／錯誤；查詢對應 API GET notification-jobs。
    """

    @abstractmethod
    def save(self, job: NotificationJob) -> None:
        """儲存或更新 NotificationJob 聚合。"""

    @abstractmethod
    def find_by_id(self, notification_job_id: UUID) -> Optional[NotificationJob]:
        """依主鍵載入；不存在則回傳 None。"""
