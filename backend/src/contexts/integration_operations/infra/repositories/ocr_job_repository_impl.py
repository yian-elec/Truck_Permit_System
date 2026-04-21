"""
OcrJobRepository 實作 — 僅使用 shared.core.db.connection.get_session()。
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from shared.core.db.connection import get_session

from src.contexts.integration_operations.domain.entities import OcrJob
from src.contexts.integration_operations.domain.repositories import OcrJobRepository
from src.contexts.integration_operations.infra.repositories._mappers import (
    ocr_job_from_rows,
    ocr_job_to_rows,
)
from src.contexts.integration_operations.infra.schema import OcrJobs, OcrResults


class OcrJobRepositoryImpl(OcrJobRepository):
    """持久化 OcrJob 聚合與其 OcrResults（以 attachment_id 關聯結果列）。"""

    def save(self, job: OcrJob) -> None:
        main, children = ocr_job_to_rows(job)
        with get_session() as session:
            session.merge(main)
            for ch in children:
                session.merge(ch)

    def find_by_id(self, ocr_job_id: UUID) -> Optional[OcrJob]:
        with get_session() as session:
            job_row = session.query(OcrJobs).filter(OcrJobs.ocr_job_id == ocr_job_id).first()
            if job_row is None:
                return None
            result_rows = (
                session.query(OcrResults)
                .filter(OcrResults.attachment_id == job_row.attachment_id)
                .order_by(OcrResults.created_at)
                .all()
            )
            return ocr_job_from_rows(job_row, result_rows)
