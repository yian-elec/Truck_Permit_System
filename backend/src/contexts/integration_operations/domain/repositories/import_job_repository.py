"""
ImportJob 儲存庫介面（Domain 埠）。

責任：匯入作業聚合的持久化；對應 ops.import_jobs 與 UC-OPS-04。
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from ..entities.import_job import ImportJob


class ImportJobRepository(ABC):
    """
    匯入作業儲存庫介面。

    用途：建立／更新 import job 狀態與摘要；查詢對應 GET import-jobs 與依 id 取得單筆。
    """

    @abstractmethod
    def save(self, job: ImportJob) -> None:
        """儲存或更新 ImportJob 聚合。"""

    @abstractmethod
    def find_by_id(self, import_job_id: UUID) -> Optional[ImportJob]:
        """依主鍵載入；不存在則回傳 None。"""
