"""
ReviewTask — 審查任務聚合根。

責任：
- 代表對 **單一 application_id** 在某一 **ReviewStage** 下之審查工作單（對應 review.review_tasks）。
- 維護 **狀態機**：待處理 → 審查中 → 已關閉；支援 **分派承辦**（assignee_user_id）與 **期限**（due_at）。
- UC-REV-01 由工廠建立；UC-REV-04／05 在決策完成後應 **關閉任務**（close）。

本聚合 **不** 內嵌決策或補件明細，僅透過 application_id 與其他聚合關聯。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.contexts.review_decision.domain.errors import InvalidReviewTaskStateError
from src.contexts.review_decision.domain.value_objects import ReviewStage, ReviewTaskStatus


@dataclass
class ReviewTask:
    """
    審查任務聚合根。

    責任欄位：
    - **review_task_id**：主鍵（由 App/Infra 產生後傳入）。
    - **application_id**：所屬申請案件。
    - **stage**／**status**：階段與生命週期狀態。
    - **assignee_user_id**：承辦人；未分派時為 None。
    - **due_at**：期限；無則 None。
    """

    review_task_id: UUID
    application_id: UUID
    stage: ReviewStage
    status: ReviewTaskStatus
    assignee_user_id: UUID | None = None
    due_at: datetime | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def open_for_application(
        cls,
        *,
        review_task_id: UUID,
        application_id: UUID,
        stage: ReviewStage,
        due_at: datetime | None,
        now: datetime,
    ) -> ReviewTask:
        """
        UC-REV-01：因 **ApplicationSubmitted**（或同等事件）建立新任務。

        責任：初始狀態 **PENDING**，尚未分派承辦。
        """
        return cls(
            review_task_id=review_task_id,
            application_id=application_id,
            stage=stage,
            status=ReviewTaskStatus.PENDING,
            assignee_user_id=None,
            due_at=due_at,
            created_at=now,
            updated_at=now,
        )

    def assign(self, assignee_user_id: UUID, now: datetime) -> None:
        """
        分派承辦人（對應 API assign 之領域操作）。

        責任：僅 **PENDING** 或 **IN_REVIEW** 允許變更承辦；**CLOSED** 禁止。
        """
        if self.status == ReviewTaskStatus.CLOSED:
            raise InvalidReviewTaskStateError(
                "cannot assign a closed review task",
                current_status=self.status.value,
            )
        self.assignee_user_id = assignee_user_id
        if self.status == ReviewTaskStatus.PENDING:
            self.status = ReviewTaskStatus.IN_REVIEW
        self._touch(now)

    def mark_in_review(self, now: datetime) -> None:
        """
        標記為審查中（無需分派承辦時可由 App 呼叫）。

        責任：**PENDING** → **IN_REVIEW**；其餘狀態拒絕。
        """
        if self.status == ReviewTaskStatus.CLOSED:
            raise InvalidReviewTaskStateError(
                "cannot mark closed task as in review",
                current_status=self.status.value,
            )
        if self.status == ReviewTaskStatus.PENDING:
            self.status = ReviewTaskStatus.IN_REVIEW
        self._touch(now)

    def close(self, now: datetime) -> None:
        """
        關閉任務（UC-REV-04 核准、UC-REV-05 駁回、或流程終止後）。

        責任：僅 **IN_REVIEW**（或允許 **PENDING** 直接關閉之簡化流程）→ **CLOSED**；
        已關閉則冪等不重複拋錯或拋錯—此處選擇 **已關閉再關閉拋錯** 以暴露重複操作。
        """
        if self.status == ReviewTaskStatus.CLOSED:
            raise InvalidReviewTaskStateError(
                "review task is already closed",
                current_status=self.status.value,
            )
        self.status = ReviewTaskStatus.CLOSED
        self._touch(now)

    def _touch(self, now: datetime) -> None:
        """更新 updated_at。"""
        self.updated_at = now
