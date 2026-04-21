"""
ImportJobRepository 實作 — 使用 get_session()。
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from shared.core.db.connection import get_session

from src.contexts.integration_operations.domain.entities import ImportJob
from src.contexts.integration_operations.domain.repositories import ImportJobRepository
from src.contexts.integration_operations.infra.repositories._mappers import (
    import_job_from_row,
    import_job_to_row,
)
from src.contexts.integration_operations.infra.schema import ImportJobs


class ImportJobRepositoryImpl(ImportJobRepository):
    """import_jobs 表的讀寫。"""

    def save(self, job: ImportJob) -> None:
        row = import_job_to_row(job)
        with get_session() as session:
            session.merge(row)

    def find_by_id(self, import_job_id: UUID) -> Optional[ImportJob]:
        with get_session() as session:
            row = session.query(ImportJobs).filter(ImportJobs.import_job_id == import_job_id).first()
            if row is None:
                return None
            return import_job_from_row(row)
