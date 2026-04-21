"""
申請案件狀態（Value Object）。

責任：與 persistence 之 status varchar(30) 對齊，集中合法狀態與轉移語意（draft／送件／補件等），
避免任意字串污染聚合。狀態機的「是否允許某行為」由 Aggregate 與本 VO 的查詢方法共同表達。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..errors import InvalidDomainValueError


class ApplicationStatusPhase(StrEnum):
    """
    申請案件在生命週期中的標準階段。

    責任：對應 `application.applications.status`（varchar(30)）之封閉集合；聚合之狀態轉移與
    「草稿可編輯／送件後鎖定／補件」等規則均依此與 `ApplicationStatus` 表達。

    成員語意摘要：
    - **DRAFT**：草稿，可編輯核心資料（見聚合 `_assert_may_mutate_case_content`）。
    - **SUBMITTED**：已送件，不可直接覆寫核心，除非進入補件流程。
    - **SUPPLEMENT_REQUIRED**：待補件，可於限制下修正可編欄位並再上傳附件。
    - **RESUBMITTED**：補件回覆後再次送出；審查前通常鎖定一般編輯。
    - **UNDER_REVIEW／APPROVED／REJECTED／CANCELLED／WITHDRAWN**：審查與結案相關階段（可隨產品擴充流程）。
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
class ApplicationStatus:
    """
    封裝持久化的 status 字串，並限制為已知階段之一。

    用途：由 Application 聚合持有；轉移時建立新實例以維持值物件不可變性。
    """

    value: str

    def __post_init__(self) -> None:
        allowed = {p.value for p in ApplicationStatusPhase}
        if self.value not in allowed:
            raise InvalidDomainValueError(
                f"Invalid application status: {self.value!r}; expected one of {sorted(allowed)}"
            )

    @classmethod
    def draft(cls) -> ApplicationStatus:
        """草稿：可編輯核心資料（在聚合規則允許範圍內）。"""
        return cls(ApplicationStatusPhase.DRAFT.value)

    @classmethod
    def submitted(cls) -> ApplicationStatus:
        """已送件：不可直接覆寫核心資料。"""
        return cls(ApplicationStatusPhase.SUBMITTED.value)

    @classmethod
    def supplement_required(cls) -> ApplicationStatus:
        """待補件：應透過補件流程更新指定項目並保留歷史。"""
        return cls(ApplicationStatusPhase.SUPPLEMENT_REQUIRED.value)

    @classmethod
    def resubmitted(cls) -> ApplicationStatus:
        """補件後再次送出，等待審查。"""
        return cls(ApplicationStatusPhase.RESUBMITTED.value)

    @classmethod
    def under_review(cls) -> ApplicationStatus:
        """審查中（承辦已受理送件／補件回覆後之審理階段）。"""
        return cls(ApplicationStatusPhase.UNDER_REVIEW.value)

    @classmethod
    def approved(cls) -> ApplicationStatus:
        """核准結案。"""
        return cls(ApplicationStatusPhase.APPROVED.value)

    @classmethod
    def rejected(cls) -> ApplicationStatus:
        """駁回結案。"""
        return cls(ApplicationStatusPhase.REJECTED.value)

    def is_draft(self) -> bool:
        return self.value == ApplicationStatusPhase.DRAFT.value

    def is_submitted(self) -> bool:
        return self.value == ApplicationStatusPhase.SUBMITTED.value

    def is_supplement_required(self) -> bool:
        return self.value == ApplicationStatusPhase.SUPPLEMENT_REQUIRED.value

    def is_resubmitted(self) -> bool:
        return self.value == ApplicationStatusPhase.RESUBMITTED.value

    def allows_full_draft_editing(self) -> bool:
        """
        是否適用「草稿級」完整核心編輯（非補件情境）。

        責任：僅有明確草稿狀態可任意編排草稿欄位；補件另有較窄規則由聚合方法處理。
        """
        return self.is_draft()
