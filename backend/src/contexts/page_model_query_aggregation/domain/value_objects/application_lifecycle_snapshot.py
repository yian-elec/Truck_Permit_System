"""
申請生命週期快照（Value Object）。

責任：由 App 層在組 Page Model 前，從 Application／Review 等 context **查完後**將精簡狀態注入領域，
使 `ApplicantApplicationEditorPageModel` 能依規則決定要露出哪些區塊（例如補件、路線編輯），
而 Domain 層仍不依赖其他 context 的 Entity 型別。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ApplicationLifecyclePhase(StrEnum):
    """
    申請案件生命週期階段（Page Model 用精簡枚舉）。

    責任：表達「申請人編輯器」區塊組版所需之決策輸入；與 Application context 持久化 status 字串
    應由 App 層對齊映射，本處不讀取資料庫。
    """

    DRAFT = "draft"
    SUBMITTED = "submitted"
    SUPPLEMENT_REQUIRED = "supplement_required"
    RESUBMITTED = "resubmitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    WITHDRAWN = "withdrawn"


@dataclass(frozen=True)
class ApplicationLifecycleSnapshot:
    """
    組「申請人編輯器 Page Model」時的領域輸入快照。

    責任：
    - 攜帶 `phase` 供規則決定是否顯示可編路線、補件回覆等區塊
    - 以旗標表達與路由／許可證相關之存在性，避免 Domain 查詢 Infra

    欄位語意：
    - **has_active_route_plan**：是否已有可展示之路線方案（影響是否強制露出路線預覽區）
    - **has_pending_supplement_request**：是否有待回覆之補件（影響補件區優先級）
    - **has_issued_permit_documents**：是否已有可關聯之許可／文件資料（影響是否露出下載區）
    """

    phase: ApplicationLifecyclePhase
    has_active_route_plan: bool = False
    has_pending_supplement_request: bool = False
    has_issued_permit_documents: bool = False

    def applicant_may_edit_case_core(self) -> bool:
        """
        申請人是否應看到「可編輯核心案件資料」區塊語意。

        責任：草稿與待補件階段允許在產品政策下編輯（實際欄位鎖定仍由 Application context 權威）；
        此處僅決定 Page Model **是否配置**對應區塊與編輯提示。
        """
        return self.phase in (
            ApplicationLifecyclePhase.DRAFT,
            ApplicationLifecyclePhase.SUPPLEMENT_REQUIRED,
        )

    def applicant_may_edit_routing(self) -> bool:
        """
        申請人是否應配置「路徑申請／方案」相關互動區塊。

        責任：草稿階段通常允許建立／調整路徑申請；補件若涉及路線則由產品與 App 映射決定，
        此處保守地僅在 **DRAFT** 與 **SUPPLEMENT_REQUIRED** 露出可編路線區（與 `applicant_may_edit_case_core` 對齊）。
        """
        return self.phase in (
            ApplicationLifecyclePhase.DRAFT,
            ApplicationLifecyclePhase.SUPPLEMENT_REQUIRED,
        )

    def should_surface_supplement_workspace(self) -> bool:
        """
        是否應在編輯器 Page Model 中突出補件工作區（列表／回覆入口）。

        責任：有待處理補件或目前處於補件階段時為 True，供聚合挑選 `REVIEW_TASKS_AND_DECISIONS` 相關區塊。
        """
        return (
            self.has_pending_supplement_request
            or self.phase == ApplicationLifecyclePhase.SUPPLEMENT_REQUIRED
        )

    def should_surface_permit_documents(self) -> bool:
        """
        是否應露出與許可證／文件下載相關之區塊。

        責任：僅當已知存在已簽發或產製中之文件關聯時為 True；避免空殼下載區。
        """
        return self.has_issued_permit_documents
