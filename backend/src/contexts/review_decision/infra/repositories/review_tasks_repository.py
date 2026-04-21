"""
ReviewTasksRepository — review.review_tasks 讀寫。

責任：僅透過 `shared.core.db.connection.get_session` 取得 session，不自建 engine／session_factory。
"""

from __future__ import annotations

from typing import List
from uuid import UUID

from sqlalchemy import select

from shared.core.db.connection import get_session

from src.contexts.review_decision.infra.repositories._orm_detach import (
    detach_all,
    detach_optional,
)
from src.contexts.review_decision.infra.schema.review_tasks import ReviewTasks


class ReviewTasksRepository:
    """審查任務表存取。"""

    def get_by_id(self, review_task_id: UUID) -> ReviewTasks | None:
        with get_session() as session:
            row = session.get(ReviewTasks, review_task_id)
            return detach_optional(session, row)

    def list_by_application_id(self, application_id: UUID) -> List[ReviewTasks]:
        with get_session() as session:
            rows = list(
                session.scalars(
                    select(ReviewTasks).where(ReviewTasks.application_id == application_id)
                ).all()
            )
            return detach_all(session, rows)

    def list_recent(self, *, limit: int = 50, offset: int = 0) -> List[ReviewTasks]:
        """
        依建立時間新到舊分頁列出審查任務（供承辦工作台／儀表板初版使用）。

        責任：大量資料時上層應改以 DB aggregate 或專用查詢取代全表掃描式計數。
        """
        with get_session() as session:
            rows = list(
                session.scalars(
                    select(ReviewTasks)
                    .order_by(ReviewTasks.created_at.desc())
                    .limit(limit)
                    .offset(offset)
                ).all()
            )
            return detach_all(session, rows)

    def add(self, row: ReviewTasks) -> ReviewTasks:
        with get_session() as session:
            session.add(row)
            session.flush()
            session.refresh(row)
            return detach_optional(session, row)

    def find_open_task_for_application(self, application_id: UUID) -> ReviewTasks | None:
        """回傳該案件第一筆非 CLOSED 之審查任務；無則 None。"""
        with get_session() as session:
            rows = list(
                session.scalars(
                    select(ReviewTasks)
                    .where(ReviewTasks.application_id == application_id)
                    .where(ReviewTasks.status != "closed")
                    .order_by(ReviewTasks.created_at)
                ).all()
            )
            if not rows:
                return None
            return detach_optional(session, rows[0])

    def update_task_row(self, row: ReviewTasks) -> ReviewTasks:
        """
        依主鍵更新已存在列（用於分派、關閉等）。

        責任：`row.review_task_id` 須已存在；更新後回傳 detached 列。
        """
        with get_session() as session:
            existing = session.get(ReviewTasks, row.review_task_id)
            if existing is None:
                return detach_optional(session, None)
            existing.stage = row.stage
            existing.status = row.status
            existing.assignee_user_id = row.assignee_user_id
            existing.due_at = row.due_at
            existing.updated_at = row.updated_at
            session.flush()
            session.refresh(existing)
            return detach_optional(session, existing)
