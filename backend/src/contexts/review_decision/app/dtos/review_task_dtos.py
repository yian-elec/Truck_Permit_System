"""
審查任務與儀表板相關 DTO（UC-REV-01、任務列表、儀表板）。

責任：與 `review.review_tasks` 及承辦工作台讀模型對齊。
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReviewTaskSummaryDTO(BaseModel):
    """單筆審查任務摘要（列表用）。"""

    model_config = ConfigDict(from_attributes=True)

    review_task_id: UUID
    application_id: UUID
    stage: str
    status: str
    assignee_user_id: UUID | None
    due_at: datetime | None
    created_at: datetime
    updated_at: datetime


class CreateReviewTaskInputDTO(BaseModel):
    """UC-REV-01：建立待審任務之輸入（事件處理或管理端觸發）。"""

    application_id: UUID
    stage: str = Field(default="initial", max_length=30)
    due_at: datetime | None = None


class CreateReviewTaskOutputDTO(BaseModel):
    """建立審查任務後回傳。"""

    review_task_id: UUID
    application_id: UUID
    stage: str
    status: str


class AssignReviewTaskInputDTO(BaseModel):
    """將案件之開放審查任務分派給承辦。"""

    assignee_user_id: UUID


class AssignReviewTaskOutputDTO(BaseModel):
    """分派結果。"""

    review_task_id: UUID
    assignee_user_id: UUID
    status: str


class ReviewDashboardDTO(BaseModel):
    """
    審查儀表板計數（初版以記憶體篩選實作）。

    責任：資料量大時應改為資料庫聚合查詢。
    """

    total_open_tasks: int
    pending_assignment_tasks: int
    in_review_tasks: int
    closed_tasks_in_window: int
