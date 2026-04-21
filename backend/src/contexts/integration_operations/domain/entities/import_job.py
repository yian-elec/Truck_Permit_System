"""
外部資料匯入作業聚合（Aggregate Root）。

責任：對應 ops.import_jobs 與 UC-OPS-04（地圖／假日／routing rules 等匯入皆為不同 job_type）；
封裝生命週期與 result_summary／error_message，與實際「抓外部資料、標準化、寫入、版本、發布」的編排分離。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from ..errors import InvalidDomainValueError, InvalidJobStateError
from ..value_objects import (
    ImportJobType,
    ImportSourceName,
    ImportSourceRef,
    JobLifecycleStatus,
)


@dataclass
class ImportJob:
    """
    匯入作業聚合根。

    責任：維護 pending → running → succeeded | failed；成功時可附結果摘要文字，
    供管理或後續查詢；終結後不可再變更狀態。
    """

    import_job_id: UUID
    job_type: ImportJobType
    source_name: ImportSourceName
    source_ref: ImportSourceRef
    status: JobLifecycleStatus
    started_at: datetime | None
    finished_at: datetime | None
    result_summary: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def schedule(
        cls,
        *,
        job_type: ImportJobType,
        source_name: ImportSourceName,
        source_ref: ImportSourceRef | None = None,
        now: datetime,
        import_job_id: UUID | None = None,
    ) -> ImportJob:
        """
        排程一筆匯入作業（建立 import job）。

        source_ref 未提供時以 ImportSourceRef(value=None) 表示資料庫 null 語意。
        """
        ref = source_ref if source_ref is not None else ImportSourceRef(value=None)
        jid = import_job_id or uuid4()
        return cls(
            import_job_id=jid,
            job_type=job_type,
            source_name=source_name,
            source_ref=ref,
            status=JobLifecycleStatus.pending(),
            started_at=None,
            finished_at=None,
            result_summary=None,
            error_message=None,
            created_at=now,
            updated_at=now,
        )

    def start(self, now: datetime) -> None:
        """開始執行匯入；僅允許自 pending 轉為 running。"""
        if self.status.value != JobLifecycleStatus.pending().value:
            raise InvalidJobStateError(
                "Only a pending import job can be started",
                current_status=self.status.value,
            )
        self.status = JobLifecycleStatus.running()
        self.started_at = now
        self.updated_at = now

    def mark_succeeded(self, summary: str | None, now: datetime) -> None:
        """
        標記匯入成功；僅允許自 running 結束。

        summary 對應 result_summary，可為 None 或空字串（由 App／DB 決定是否存 null）。
        """
        if self.status.value != JobLifecycleStatus.running().value:
            raise InvalidJobStateError(
                "Only a running import job can succeed",
                current_status=self.status.value,
            )
        self.status = JobLifecycleStatus.succeeded()
        self.finished_at = now
        self.error_message = None
        self.result_summary = summary.strip() if summary and summary.strip() else None
        self.updated_at = now

    def mark_failed(self, message: str, now: datetime) -> None:
        """標記匯入失敗；可由 pending 或 running 轉入 failed。"""
        if self.status.is_terminal():
            raise InvalidJobStateError(
                "Cannot fail an import job that has already finished",
                current_status=self.status.value,
            )
        if not message or not message.strip():
            raise InvalidDomainValueError("Failure message is required for a failed import job")
        self.status = JobLifecycleStatus.failed()
        self.error_message = message.strip()
        self.finished_at = now
        self.updated_at = now
