"""
SupplementRequest — 補件請求聚合根。

責任：
- 封裝 **review.supplement_requests**（必要時搭配 **review.supplement_items** 之舊資料）之領域生命週期：
  發出（OPEN）、完成（FULFILLED）、作廢（CANCELLED）。
- **items** 可為空（現行產品僅「標題 + 說明正文」）；UC-REV-03 由工廠 **issue** 建立。
- **title**／**message**：對外短標題與詳細說明；**deadline_at** 可為 None。

本聚合 **不** 直接修改 Application context 之狀態；僅表達補件領域事實，由 App 層呼叫
Application 服務更新為 supplement_required。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.contexts.review_decision.domain.errors import (
    InvalidSupplementRequestStateError,
    ReviewInvalidValueError,
)
from src.contexts.review_decision.domain.value_objects import (
    SupplementItem,
    SupplementRequestStatus,
)


@dataclass
class SupplementRequest:
    """
    補件請求聚合根。

    責任欄位：
    - **supplement_request_id**：主鍵。
    - **application_id**／**requested_by**：案件與發起承辦。
    - **deadline_at**／**status**／**title**／**message**：期限、狀態、短標題、對外說明。
    - **items**：補件項目列（值物件，可為空）；建立後以 tuple 固定。
    """

    supplement_request_id: UUID
    application_id: UUID
    requested_by: UUID
    deadline_at: datetime | None
    status: SupplementRequestStatus
    title: str
    message: str
    items: tuple[SupplementItem, ...]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def issue(
        cls,
        *,
        supplement_request_id: UUID,
        application_id: UUID,
        requested_by: UUID,
        deadline_at: datetime | None,
        title: str,
        message: str,
        items: tuple[SupplementItem, ...],
        now: datetime,
    ) -> SupplementRequest:
        """
        UC-REV-03：發出補件（標題 + 正文；項目列可為空）。

        責任：
        - **title**／**message** 不可空白。
        """
        ttl = (title or "").strip()
        if not ttl:
            raise ReviewInvalidValueError("supplement title must be non-empty")
        if len(ttl) > 200:
            raise ReviewInvalidValueError("supplement title exceeds max length")
        msg = (message or "").strip()
        if not msg:
            raise ReviewInvalidValueError("supplement message must be non-empty")
        if len(msg) > 20_000:
            raise ReviewInvalidValueError("supplement message exceeds max length")

        return cls(
            supplement_request_id=supplement_request_id,
            application_id=application_id,
            requested_by=requested_by,
            deadline_at=deadline_at,
            status=SupplementRequestStatus.OPEN,
            title=ttl,
            message=msg,
            items=tuple(items),
            created_at=now,
            updated_at=now,
        )

    def fulfill(self, now: datetime) -> None:
        """
        標記補件請求已完成（由 App 依申請人回覆或人工確認後呼叫）。

        責任：僅 **OPEN** → **FULFILLED**。
        """
        self._require_open()
        self.status = SupplementRequestStatus.FULFILLED
        self._touch(now)

    def cancel(self, now: datetime) -> None:
        """
        作廢補件請求（例如案件駁回後不再等待補件）。

        責任：**OPEN** → **CANCELLED**；已終結狀態不可再變更。
        """
        self._require_open()
        self.status = SupplementRequestStatus.CANCELLED
        self._touch(now)

    def _require_open(self) -> None:
        if self.status != SupplementRequestStatus.OPEN:
            raise InvalidSupplementRequestStateError(
                f"supplement request must be OPEN, got {self.status.value}"
            )

    def _touch(self, now: datetime) -> None:
        self.updated_at = now
