"""
申請案件讀模型查詢埠（Domain）。

責任：對應規格 5.2 之 **ApplicationReadModelQuery**——承載**不必載入完整 Write 聚合**
即可回答的查詢（列表、附件摘要等）。由 Infra 以 SQL／投影表實作；
與 `ApplicationRepository`（載入／儲存聚合）分離，符合 CQRS 式邊界。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from ..read_models import AttachmentSummaryView


class ApplicationReadModelQuery(ABC):
    """
    Application 讀模型查詢抽象。

    責任：宣告唯讀查詢契約供 App 層注入。
    """

    @abstractmethod
    def list_application_ids_for_applicant(
        self, applicant_user_id: UUID, *, limit: int = 100
    ) -> list[UUID]:
        """
        依申請人使用者 ID 列出案件主鍵（新在前）。

        責任：供 GET /applicant/applications 列表；不需載入完整聚合。
        """

    @abstractmethod
    def list_attachment_summaries(self, application_id: UUID) -> list[AttachmentSummaryView]:
        """
        列出指定案件之附件中繼資料（對應 application.attachments）。

        責任：供 API 附件列表與案件明細組裝；不載入完整聚合。
        """
