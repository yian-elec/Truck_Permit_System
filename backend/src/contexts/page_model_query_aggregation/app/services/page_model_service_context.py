"""
Page Model 用例服務之依賴聚合（Service Context）。

責任：注入 `PageModelSectionCatalog` 與可選之 `PageModelSnapshotsRepository`，
讓 `PageModelQueryApplicationService` 可測試替換依賴，並與 Infra 解耦（repository 為可選 None）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src.contexts.page_model_query_aggregation.domain.services.page_model_section_catalog import (
    PageModelSectionCatalog,
)

if TYPE_CHECKING:
    from src.contexts.page_model_query_aggregation.infra.repositories.page_model_snapshots_repository import (
        PageModelSnapshotsRepository,
    )


@dataclass
class PageModelServiceContext:
    """
    應用服務執行所需之唯讀／可選寫入依賴。

    責任：
    - **section_catalog**：Domain 組版時驗證區塊代碼之封閉目錄（預設為 `default()`）。
    - **snapshots_repository**：若提供，則可依用例選擇性寫入／讀取快取列（最佳努力，失敗不影響主流程時由呼叫端決定）。
    """

    section_catalog: PageModelSectionCatalog = field(default_factory=PageModelSectionCatalog.default)
    snapshots_repository: PageModelSnapshotsRepository | None = None
