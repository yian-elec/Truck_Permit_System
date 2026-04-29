"""
領域聚合與 review schema ORM 之轉換。

責任：與 Application context 之 `application_mappers.py` 角色對齊——集中 DTO／領域 ↔ 持久化形狀，
避免命令服務腫脹；不含用例流程或業務分支。
"""

from __future__ import annotations

from uuid import UUID

from src.contexts.review_decision.domain.entities import (
    ReviewDecision,
    ReviewTask,
    SupplementRequest,
)
from src.contexts.review_decision.domain.value_objects import (
    ReviewStage,
    ReviewTaskStatus,
    SupplementItem,
)
from src.contexts.review_decision.infra.schema.decisions import Decisions
from src.contexts.review_decision.infra.schema.review_tasks import ReviewTasks
from src.contexts.review_decision.infra.schema.supplement_items import SupplementItems
from src.contexts.review_decision.infra.schema.supplement_requests import SupplementRequests


def orm_review_task_to_domain(row: ReviewTasks) -> ReviewTask:
    """ORM 列 → ReviewTask 領域（用於載入後分派／關閉）。"""
    return ReviewTask(
        review_task_id=row.review_task_id,
        application_id=row.application_id,
        stage=ReviewStage(row.stage),
        status=ReviewTaskStatus(row.status),
        assignee_user_id=row.assignee_user_id,
        due_at=row.due_at,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def domain_review_task_to_orm(task: ReviewTask) -> ReviewTasks:
    """ReviewTask 領域 → ORM 列。"""
    return ReviewTasks(
        review_task_id=task.review_task_id,
        application_id=task.application_id,
        stage=task.stage.value,
        status=task.status.value,
        assignee_user_id=task.assignee_user_id,
        due_at=task.due_at,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


def domain_review_decision_to_orm(d: ReviewDecision) -> Decisions:
    """ReviewDecision 領域 → ORM 列。"""
    return Decisions(
        decision_id=d.decision_id,
        application_id=d.application_id,
        decision_type=d.decision_type.value,
        selected_candidate_id=d.selected_candidate_id,
        override_id=d.override_id,
        approved_start_at=d.approved_period.start_at if d.approved_period else None,
        approved_end_at=d.approved_period.end_at if d.approved_period else None,
        reason=d.reason,
        decided_by=d.decided_by,
        decided_at=d.decided_at,
        created_at=d.created_at,
    )


def domain_supplement_request_to_orm(sr: SupplementRequest) -> SupplementRequests:
    """SupplementRequest 聚合 → 請求主檔 ORM。"""
    return SupplementRequests(
        supplement_request_id=sr.supplement_request_id,
        application_id=sr.application_id,
        requested_by=sr.requested_by,
        deadline_at=sr.deadline_at,
        status=sr.status.value,
        title=sr.title,
        message=sr.message,
        created_at=sr.created_at,
        updated_at=sr.updated_at,
    )


def supplement_item_vo_to_orm(
    *,
    supplement_item_id: UUID,
    supplement_request_id: UUID,
    item: SupplementItem,
    created_at,
) -> SupplementItems:
    """單一補件項目值物件 → ORM 列。"""
    return SupplementItems(
        supplement_item_id=supplement_item_id,
        supplement_request_id=supplement_request_id,
        item_code=item.item_code,
        item_name=item.item_name,
        required_action=item.required_action.value,
        note=item.note,
        created_at=created_at,
    )
