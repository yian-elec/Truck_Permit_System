"""
DocumentGenerationJob — 文件產製工作單實體（對應 permit.document_jobs）。

責任：表達 worker 可撿取之產檔任務生命週期（PENDING→PROCESSING→COMPLETED／FAILED）；
**FAILED** 時保留 error_message；**不** 在此實體內修改 Permit 核准相關狀態，
由 App 呼叫 Permit 聚合之方法以標示「待補產」。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.contexts.permit_document.domain.errors import DocumentJobStateError
from src.contexts.permit_document.domain.value_objects import (
    DocumentJobStatus,
    DocumentJobStatusPhase,
    DocumentJobType,
)


@dataclass
class DocumentGenerationJob:
    """
    單一產檔工作列（聚合內實體，或與 Permit 同生命週期叢集）。

    責任欄位：job_id, application_id, permit_id?, job_type, status, error_message, created_at, updated_at。
    """

    job_id: UUID
    application_id: UUID
    permit_id: UUID | None
    job_type: DocumentJobType
    status: DocumentJobStatus
    error_message: str | None
    created_at: datetime
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def enqueue(
        cls,
        *,
        job_id: UUID,
        application_id: UUID,
        permit_id: UUID | None,
        job_type: DocumentJobType,
        now: datetime,
    ) -> DocumentGenerationJob:
        """
        建立待處理工作單（UC-PERMIT-01 建立 document jobs）。

        責任：初始 **PENDING**；permit_id 在 permit 建立前可為 None，建議 App 後續補齊或建立時即帶入。
        """
        return cls(
            job_id=job_id,
            application_id=application_id,
            permit_id=permit_id,
            job_type=job_type,
            status=DocumentJobStatus(DocumentJobStatusPhase.PENDING.value),
            error_message=None,
            created_at=now,
            updated_at=now,
        )

    def mark_processing(self, now: datetime) -> None:
        """Worker 開始處理：PENDING → PROCESSING。"""
        self._require_status(DocumentJobStatusPhase.PENDING.value)
        self.status = DocumentJobStatus(DocumentJobStatusPhase.PROCESSING.value)
        self._touch(now)

    def mark_completed(self, now: datetime) -> None:
        """成功完成：PROCESSING → COMPLETED。"""
        self._require_status(DocumentJobStatusPhase.PROCESSING.value)
        self.status = DocumentJobStatus(DocumentJobStatusPhase.COMPLETED.value)
        self.error_message = None
        self._touch(now)

    def mark_failed(self, message: str, now: datetime) -> None:
        """
        失敗：PROCESSING → FAILED，寫入 error_message。

        責任：不回滾外部核准；呼叫端應再驅動 Permit 聚合標示待補產（若適用）。
        """
        self._require_status(DocumentJobStatusPhase.PROCESSING.value)
        self.status = DocumentJobStatus(DocumentJobStatusPhase.FAILED.value)
        self.error_message = message
        self._touch(now)

    def _require_status(self, expected: str) -> None:
        if self.status.value != expected:
            raise DocumentJobStateError(
                f"expected job status {expected!r}, got {self.status.value!r}",
                details={"job_id": str(self.job_id), "current_status": self.status.value},
            )

    def _touch(self, now: datetime) -> None:
        self.updated_at = now
