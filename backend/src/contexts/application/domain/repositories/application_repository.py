"""
申請案件儲存庫介面（Domain）。

責任：定義聚合之載入與持久化契約；實作類別置於 infra.repositories，僅能透過
repository 邊界存取 DB，Domain 不引用 SQLAlchemy 或連線。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from ..entities import Application


class ApplicationRepository(ABC):
    """
    Application 聚合之讀寫埠。

    責任：維持「一筆 application_id 對應一完整聚合」之載入語意；save 應以單一交易
    寫回聚合內變更（含子實體與附件組），由 Infra 對照 ORM schema。
    """

    @abstractmethod
    def get_by_id(self, application_id: UUID) -> Application | None:
        """
        依主鍵載入完整聚合（含 profiles、vehicles、bundle、histories 等視圖）。

        責任：找不到時回傳 None，不拋錯。
        """

    @abstractmethod
    def get_by_application_no(self, application_no: str) -> Application | None:
        """
        依對外案件編號載入聚合。

        責任：供查詢與幕等建立（避免重複 application_no）時使用。
        """

    @abstractmethod
    def save(self, application: Application) -> None:
        """
        持久化聚合之變更（新增或更新）。

        責任：實作需處理 version 樂觀鎖與子表差異寫入；衝突時由 Infra 轉為可辨識例外。
        """
