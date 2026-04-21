"""
OCR 作業聚合（Aggregate Root）與辨識結果實體。

責任：
- OcrJob：對應 ops.ocr_jobs，封裝 UC-OPS-01 的狀態與不變條件（何時可開始、寫入結果、結束）。
- OcrResult：對應 ops.ocr_results，屬於本聚合內的實體，透過 OcrJob 統一新增，維護與附件／作業的一致性。

attachment_id 為他界（例如檔案／附件 context）的識別，此處僅以 UUID 持有，不驗證外部是否存在。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from ..errors import InvalidDomainValueError, InvalidJobStateError
from ..value_objects import (
    Confidence,
    JobLifecycleStatus,
    OcrFieldName,
    OcrProviderCode,
)


@dataclass(frozen=True)
class OcrResult:
    """
    單一欄位辨識結果（聚合內實體）。

    責任：保存 attachment_id（對齊 ops.ocr_results.attachment_id）、field_name、field_value、
    confidence、raw_json 與建立時間；建立後不可變，避免竄改歷史辨識紀錄。
    """

    ocr_result_id: UUID
    attachment_id: UUID
    field_name: OcrFieldName
    field_value: str | None
    confidence: Confidence | None
    raw_json: dict[str, Any] | None
    created_at: datetime

    @classmethod
    def new(
        cls,
        *,
        attachment_id: UUID,
        field_name: OcrFieldName,
        field_value: str | None,
        confidence: Confidence | None,
        raw_json: dict[str, Any] | None,
        created_at: datetime,
        ocr_result_id: UUID | None = None,
    ) -> OcrResult:
        """建立一筆新辨識結果（ID 未給則由領域產生 UUID）。"""
        return cls(
            ocr_result_id=ocr_result_id or uuid4(),
            attachment_id=attachment_id,
            field_name=field_name,
            field_value=field_value,
            confidence=confidence,
            raw_json=raw_json,
            created_at=created_at,
        )


@dataclass
class OcrJob:
    """
    OCR 作業聚合根（Aggregate Root）。

    責任：
    - 維護作業生命週期：pending → running → succeeded | failed。
    - 僅在 running 時允許附加 OcrResult（解析車號、日期、公司名等寫入結果）。
    - 終結後不可再變更狀態或新增結果。
    """

    ocr_job_id: UUID
    attachment_id: UUID
    provider_code: OcrProviderCode
    status: JobLifecycleStatus
    started_at: datetime | None
    finished_at: datetime | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
    _results: list[OcrResult] = field(default_factory=list, repr=False)

    @property
    def results(self) -> tuple[OcrResult, ...]:
        """對外唯讀檢視聚合內辨識結果（不可直接修改 list 參考）。"""
        return tuple(self._results)

    @classmethod
    def schedule(
        cls,
        *,
        attachment_id: UUID,
        provider_code: OcrProviderCode,
        now: datetime,
        ocr_job_id: UUID | None = None,
    ) -> OcrJob:
        """
        因 AttachmentUploaded 等事件而排程一筆 OCR 作業（對應建立 ocr job）。

        初始狀態為 pending；實際從 storage 取檔與呼叫 provider 由 App 層編排。
        """
        jid = ocr_job_id or uuid4()
        st = JobLifecycleStatus.pending()
        return cls(
            ocr_job_id=jid,
            attachment_id=attachment_id,
            provider_code=provider_code,
            status=st,
            started_at=None,
            finished_at=None,
            error_message=None,
            created_at=now,
            updated_at=now,
            _results=[],
        )

    def start(self, now: datetime) -> None:
        """標記作業開始（設定 started_at）；僅允許自 pending 轉為 running。"""
        if self.status.value != JobLifecycleStatus.pending().value:
            raise InvalidJobStateError(
                "Only a pending OCR job can be started",
                current_status=self.status.value,
            )
        self.status = JobLifecycleStatus.running()
        self.started_at = now
        self.updated_at = now

    def add_result(self, result: OcrResult) -> None:
        """
        寫入一筆辨識結果至聚合內。

        僅在 running 時允許，對應解析後寫入 ocr_results 的領域規則。
        """
        if self.status.value != JobLifecycleStatus.running().value:
            raise InvalidJobStateError(
                "OCR results can only be added while the job is running",
                current_status=self.status.value,
            )
        if result.attachment_id != self.attachment_id:
            raise InvalidDomainValueError(
                "OcrResult.attachment_id must match the OcrJob.attachment_id for this aggregate"
            )
        self._results.append(result)
        self.updated_at = result.created_at

    def mark_succeeded(self, now: datetime) -> None:
        """標記作業成功完成；僅允許自 running 結束。"""
        if self.status.value != JobLifecycleStatus.running().value:
            raise InvalidJobStateError(
                "Only a running OCR job can succeed",
                current_status=self.status.value,
            )
        self.status = JobLifecycleStatus.succeeded()
        self.finished_at = now
        self.error_message = None
        self.updated_at = now

    def mark_failed(self, message: str, now: datetime) -> None:
        """標記作業失敗並保存錯誤訊息；可由 pending 或 running 轉入 failed。"""
        if self.status.is_terminal():
            raise InvalidJobStateError(
                "Cannot fail a job that has already finished",
                current_status=self.status.value,
            )
        if not message or not message.strip():
            raise InvalidDomainValueError("Failure message is required for a failed OCR job")
        self.status = JobLifecycleStatus.failed()
        self.error_message = message.strip()
        self.finished_at = now
        self.updated_at = now
