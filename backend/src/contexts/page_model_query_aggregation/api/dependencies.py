"""
Page_Model_Query_Aggregation — API 依賴注入。

責任：
- 組裝 `PageModelQueryApplicationService`（可擴充注入快照 Repository 以啟用快取）；
- 申請人端沿用 **Application** 之 `get_applicant_user_id`；
- 審查／管理端沿用 **Review_Decision** 之 `get_officer_user_id`（JWT `sub` 映射規則相同，實際 RBAC 由政策擴充）。
"""

from __future__ import annotations

from src.contexts.application.api.dependencies import get_applicant_user_id
from src.contexts.page_model_query_aggregation.app.services import (
    PageModelQueryApplicationService,
    PageModelServiceContext,
)
from src.contexts.review_decision.api.dependencies import get_officer_user_id


def get_page_model_query_application_service() -> PageModelQueryApplicationService:
    """
    建立 Page Model 查詢應用服務（預設不注入快照 Repository，每次由 Domain 組版）。

    責任：若日後需全站快取，可改為 `PageModelServiceContext(snapshots_repository=...)`。
    """
    return PageModelQueryApplicationService(PageModelServiceContext())


# 語意別名：OpenAPI／路由註解可區分「申請人」「承辦」「管理後台」角色，解析邏輯相同。
get_page_model_applicant_user_id = get_applicant_user_id
get_page_model_officer_user_id = get_officer_user_id
"""審查端 Page Model：JWT → 使用者 UUID。"""
get_page_model_admin_user_id = get_officer_user_id
"""管理端儀表板 Page Model：與承辦相同之 JWT 主體解析（角色檢查另由授權模組擴充）。"""
