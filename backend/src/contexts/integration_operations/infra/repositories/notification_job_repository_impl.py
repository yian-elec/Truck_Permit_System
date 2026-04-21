"""
NotificationJobRepository 實作 — 使用 get_session()。
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from shared.core.db.connection import get_session

from src.contexts.integration_operations.domain.entities import NotificationJob
from src.contexts.integration_operations.domain.repositories import NotificationJobRepository
from src.contexts.integration_operations.infra.repositories._mappers import (
    notification_job_from_row,
    notification_job_to_row,
)
from src.contexts.integration_operations.infra.schema import NotificationJobs


class NotificationJobRepositoryImpl(NotificationJobRepository):
    """notification_jobs 表的讀寫。"""

    def save(self, job: NotificationJob) -> None:
        row = notification_job_to_row(job)
        with get_session() as session:
            session.merge(row)

    def find_by_id(self, notification_job_id: UUID) -> Optional[NotificationJob]:
        with get_session() as session:
            row = (
                session.query(NotificationJobs)
                .filter(NotificationJobs.notification_job_id == notification_job_id)
                .first()
            )
            if row is None:
                return None
            return notification_job_from_row(row)
