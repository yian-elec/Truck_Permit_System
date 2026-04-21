"""
UC-OPS-01 — OCR 附件用例服務。

責任：
- 排程 ocr job（Domain 建立 + Repository 持久化）。
- 執行管線：取檔 → OCR → 寫入 ocr_results（經 Domain）→ 更新狀態 → 可選回寫附件 ocr_status。

交易：單次 Repository.save 觸發一筆 DB 交易；管線中失敗時嘗試 mark_failed 再 save 一次。
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from shared.core.logger.logger import logger

from src.contexts.integration_operations.app.dtos import (
    OcrExtractedFieldDTO,
    RunOcrPipelineInputDTO,
    RunOcrPipelineOutputDTO,
    ScheduleOcrJobInputDTO,
    ScheduleOcrJobOutputDTO,
)
from src.contexts.integration_operations.app.errors import (
    OpsConflictError,
    OpsExternalDependencyError,
    OpsResourceNotFoundError,
)
from src.contexts.integration_operations.domain.entities import OcrJob, OcrResult
from src.contexts.integration_operations.domain.errors import InvalidDomainValueError, InvalidJobStateError
from src.contexts.integration_operations.domain.repositories import OcrJobRepository
from src.contexts.integration_operations.domain.value_objects import Confidence, OcrFieldName, OcrProviderCode

from .ports import AttachmentBlobPort, AttachmentOcrStatusPort, OcrExtractorPort


class OcrAttachmentApplicationService:
    """協調 OCR 領域聚合與外部埠的應用服務。"""

    def __init__(
        self,
        ocr_job_repository: OcrJobRepository,
        attachment_blob_port: AttachmentBlobPort,
        ocr_extractor_port: OcrExtractorPort,
        attachment_ocr_status_port: Optional[AttachmentOcrStatusPort] = None,
    ) -> None:
        self._ocr_repo = ocr_job_repository
        self._blobs = attachment_blob_port
        self._ocr_engine = ocr_extractor_port
        self._attachment_status = attachment_ocr_status_port

    def schedule_after_attachment_uploaded(self, dto: ScheduleOcrJobInputDTO) -> ScheduleOcrJobOutputDTO:
        """
        AttachmentUploaded 事件後建立 OCR 作業。

        流程：組合 VO → Domain.schedule → Repository.save → 輸出 DTO。
        """
        now = datetime.now(timezone.utc)
        logger.info(
            "OcrAttachmentApplicationService.schedule_after_attachment_uploaded "
            f"attachment_id={dto.attachment_id}"
        )
        try:
            job = OcrJob.schedule(
                attachment_id=dto.attachment_id,
                provider_code=OcrProviderCode(dto.provider_code),
                now=now,
            )
        except InvalidDomainValueError as e:
            logger.warn(f"OCR schedule validation failed: {e}")
            raise

        self._ocr_repo.save(job)
        return ScheduleOcrJobOutputDTO(
            ocr_job_id=job.ocr_job_id,
            status=job.status.value,
            attachment_id=job.attachment_id,
        )

    def run_ocr_pipeline(self, dto: RunOcrPipelineInputDTO) -> RunOcrPipelineOutputDTO:
        """
        執行 OCR 管線（取檔、辨識、寫結果、成功／失敗結束）。

        錯誤：找不到 job → OpsResourceNotFoundError；外部埠失敗 → OpsExternalDependencyError 並盡力標記 job failed。
        """
        now = datetime.now(timezone.utc)
        job = self._ocr_repo.find_by_id(dto.ocr_job_id)
        if job is None:
            raise OpsResourceNotFoundError(f"OCR job not found: {dto.ocr_job_id}")

        def _fail(msg: str, exc: Exception | None = None) -> None:
            safe = (msg or "OCR pipeline failed").strip() or "OCR pipeline failed"
            try:
                job.mark_failed(safe[:20000], now)
                self._ocr_repo.save(job)
            except (InvalidJobStateError, InvalidDomainValueError) as inner:
                logger.error(f"Could not persist failed OCR job state: {inner}")
            if self._attachment_status:
                try:
                    self._attachment_status.update_ocr_status(
                        attachment_id=job.attachment_id,
                        status="failed",
                        error_message=safe[:2000],
                    )
                except Exception as inner:
                    logger.error(f"attachment ocr status callback failed: {inner}")
            if exc:
                raise OpsExternalDependencyError(safe, details={"cause": type(exc).__name__}) from exc
            raise OpsExternalDependencyError(safe)

        try:
            job.start(now)
        except InvalidJobStateError as e:
            logger.warn(f"OCR start invalid state job={dto.ocr_job_id}: {e}")
            raise OpsConflictError(str(e), details={"ocr_job_id": str(dto.ocr_job_id)}) from e

        try:
            blob = self._blobs.fetch_attachment_bytes(job.attachment_id)
        except Exception as e:
            logger.error(f"fetch_attachment_bytes failed: {e}")
            _fail(f"storage fetch failed: {e}", e)

        try:
            fields: list[OcrExtractedFieldDTO] = self._ocr_engine.extract_fields(
                image_bytes=blob,
                provider_code=job.provider_code.value,
            )
        except Exception as e:
            logger.error(f"ocr extract_fields failed: {e}")
            _fail(f"ocr provider failed: {e}", e)

        for f in fields:
            try:
                conf = Confidence.from_float(f.confidence) if f.confidence is not None else None
                result = OcrResult.new(
                    attachment_id=job.attachment_id,
                    field_name=OcrFieldName(f.field_name),
                    field_value=f.field_value,
                    confidence=conf,
                    raw_json=f.raw_json,
                    created_at=datetime.now(timezone.utc),
                )
                job.add_result(result)
            except (InvalidDomainValueError, InvalidJobStateError) as e:
                _fail(f"invalid ocr field payload: {e}")

        try:
            job.mark_succeeded(now)
        except InvalidJobStateError as e:
            _fail(f"cannot complete ocr job: {e}")

        self._ocr_repo.save(job)

        if self._attachment_status:
            try:
                self._attachment_status.update_ocr_status(
                    attachment_id=job.attachment_id,
                    status="succeeded",
                    error_message=None,
                )
            except Exception as e:
                logger.error(f"attachment ocr status success callback failed: {e}")

        return RunOcrPipelineOutputDTO(
            ocr_job_id=job.ocr_job_id,
            status=job.status.value,
            result_count=len(job.results),
        )
