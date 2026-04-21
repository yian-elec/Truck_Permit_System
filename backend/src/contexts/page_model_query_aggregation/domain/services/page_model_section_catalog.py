"""
Page 區塊代碼目錄（Domain Service）。

責任：維護本 bounded context **允許使用**的 `PageSectionCode` 封閉集合，並在聚合組版時驗證
所有區塊均已登記，避免 App 層拼錯代碼導致前端與契約漂移。不負責實際查詢資料。
"""

from __future__ import annotations

from dataclasses import dataclass

from ..errors import UnknownSectionCodeError
from ..value_objects import PageSectionCode


# --- 申請人首頁 -----------------------------------------------------------------
HOME_SERVICE_OVERVIEW = PageSectionCode("applicant.home.service_overview")
HOME_USER_ACCOUNT = PageSectionCode("applicant.home.user_account")
HOME_MY_APPLICATIONS = PageSectionCode("applicant.home.my_applications")
HOME_OPS_ACTIVITY_SNAPSHOT = PageSectionCode("applicant.home.ops_activity_snapshot")

# --- 申請人編輯器 --------------------------------------------------------------
EDITOR_CASE_CORE = PageSectionCode("applicant.editor.case_core")
EDITOR_VEHICLES = PageSectionCode("applicant.editor.vehicles")
EDITOR_ATTACHMENTS = PageSectionCode("applicant.editor.attachments")
EDITOR_ROUTING = PageSectionCode("applicant.editor.routing")
EDITOR_SUPPLEMENT_WORKSPACE = PageSectionCode("applicant.editor.supplement_workspace")
EDITOR_PERMIT_DOCUMENTS = PageSectionCode("applicant.editor.permit_documents")

# --- 審查頁 -------------------------------------------------------------------
REVIEW_CASE_READONLY = PageSectionCode("review.application.case_readonly")
REVIEW_ROUTING_READONLY = PageSectionCode("review.application.routing_readonly")
REVIEW_WORKSPACE = PageSectionCode("review.application.review_workspace")
REVIEW_PERMIT_READONLY = PageSectionCode("review.application.permit_readonly")

# --- 管理儀表板 ---------------------------------------------------------------
ADMIN_METRICS = PageSectionCode("admin.dashboard.metrics")
ADMIN_OPS_FEED = PageSectionCode("admin.dashboard.ops_feed")


@dataclass(frozen=True)
class PageModelSectionCatalog:
    """
    區塊代碼登錄簿（領域服務實例，可於測試替換為子集）。

    責任：`assert_all_registered` 接受一組 `PageSectionCode`，若有任一不在目錄則拋錯；
    預設實例包含本 context 規格已定義之全部代碼。
    """

    known_codes: frozenset[PageSectionCode]

    @classmethod
    def default(cls) -> PageModelSectionCatalog:
        """建立含完整預設代碼集之目錄。"""
        return cls(
            known_codes=frozenset(
                {
                    HOME_SERVICE_OVERVIEW,
                    HOME_USER_ACCOUNT,
                    HOME_MY_APPLICATIONS,
                    HOME_OPS_ACTIVITY_SNAPSHOT,
                    EDITOR_CASE_CORE,
                    EDITOR_VEHICLES,
                    EDITOR_ATTACHMENTS,
                    EDITOR_ROUTING,
                    EDITOR_SUPPLEMENT_WORKSPACE,
                    EDITOR_PERMIT_DOCUMENTS,
                    REVIEW_CASE_READONLY,
                    REVIEW_ROUTING_READONLY,
                    REVIEW_WORKSPACE,
                    REVIEW_PERMIT_READONLY,
                    ADMIN_METRICS,
                    ADMIN_OPS_FEED,
                }
            )
        )

    def assert_all_registered(self, codes: tuple[PageSectionCode, ...]) -> None:
        """
        驗證所有代碼均已登記。

        責任：聚合根在 `compose` 完成後呼叫，保證輸出之契約僅使用受控代碼。
        """
        for c in codes:
            if c not in self.known_codes:
                raise UnknownSectionCodeError(
                    f"PageSectionCode not registered in catalog: {c.value}",
                    code=c.value,
                )
