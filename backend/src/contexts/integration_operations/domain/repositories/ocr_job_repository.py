"""
OcrJob 儲存庫介面（Domain 埠）。

責任：定義聚合根 OcrJob 的持久化契約；實作屬於 Infra，領域僅依賴此抽象。
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from ..entities.ocr_job import OcrJob


class OcrJobRepository(ABC):
    """
    OCR 作業儲存庫介面。

    用途：支援 UC-OPS-01 建立／更新 job 與關聯結果的持久化；查詢方法對應 API GET ocr-jobs。
    """

    @abstractmethod
    def save(self, job: OcrJob) -> None:
        """儲存或更新整個 OcrJob 聚合（含其 OcrResult 集合）。"""

    @abstractmethod
    def find_by_id(self, ocr_job_id: UUID) -> Optional[OcrJob]:
        """依主鍵載入聚合；不存在則回傳 None。"""
