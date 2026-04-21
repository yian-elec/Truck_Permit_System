"""
UC-OPS-04 — 外部資料匯入用例服務。

責任：排程 import job、執行管線（委由 ImportIngestionPort 完成抓數／標準化／落地）、更新作業狀態。
"""

from __future__ import annotations

from datetime import datetime, timezone

from shared.core.logger.logger import logger

from src.contexts.integration_operations.app.dtos import (
    RunImportPipelineInputDTO,
    RunImportPipelineOutputDTO,
    ScheduleImportJobInputDTO,
    ScheduleImportJobOutputDTO,
)
from src.contexts.integration_operations.app.errors import OpsConflictError, OpsExternalDependencyError, OpsResourceNotFoundError
from src.contexts.integration_operations.domain.entities import ImportJob
from src.contexts.integration_operations.domain.errors import InvalidDomainValueError, InvalidJobStateError
from src.contexts.integration_operations.domain.repositories import ImportJobRepository
from src.contexts.integration_operations.domain.value_objects import ImportJobType, ImportSourceName, ImportSourceRef

from .ports import ImportIngestionPort


class ImportApplicationService:
    """協調匯入聚合、Repository 與落地埠。"""

    def __init__(
        self,
        import_job_repository: ImportJobRepository,
        ingestion_port: ImportIngestionPort,
    ) -> None:
        self._repo = import_job_repository
        self._ingest = ingestion_port

    def schedule_import(self, dto: ScheduleImportJobInputDTO) -> ScheduleImportJobOutputDTO:
        """建立 import job（pending）。"""
        now = datetime.now(timezone.utc)
        logger.info(
            "ImportApplicationService.schedule_import "
            f"type={dto.job_type} source={dto.source_name}"
        )
        try:
            source_ref_vo: ImportSourceRef | None = (
                ImportSourceRef(value=dto.source_ref) if dto.source_ref is not None else None
            )
            job = ImportJob.schedule(
                job_type=ImportJobType(dto.job_type),
                source_name=ImportSourceName(dto.source_name),
                source_ref=source_ref_vo,
                now=now,
            )
        except InvalidDomainValueError as e:
            logger.warn(f"import schedule validation failed: {e}")
            raise

        self._repo.save(job)
        return ScheduleImportJobOutputDTO(import_job_id=job.import_job_id, status=job.status.value)

    def run_import_pipeline(self, dto: RunImportPipelineInputDTO) -> RunImportPipelineOutputDTO:
        """執行匯入：start → ingest → succeeded／failed。"""
        now = datetime.now(timezone.utc)
        job = self._repo.find_by_id(dto.import_job_id)
        if job is None:
            raise OpsResourceNotFoundError(f"import job not found: {dto.import_job_id}")

        try:
            job.start(now)
        except InvalidJobStateError as e:
            raise OpsConflictError(str(e), details={"import_job_id": str(dto.import_job_id)}) from e

        self._repo.save(job)

        try:
            summary = self._ingest.ingest(
                import_job_id=job.import_job_id,
                job_type=job.job_type.value,
                source_name=job.source_name.value,
                source_ref=job.source_ref.value,
            )
        except Exception as e:
            logger.error(f"import ingestion failed: {e}")
            try:
                job.mark_failed(str(e)[:20000], datetime.now(timezone.utc))
                self._repo.save(job)
            except (InvalidJobStateError, InvalidDomainValueError):
                logger.error("could not persist import job failure state")
            raise OpsExternalDependencyError(
                f"import ingestion failed: {e}",
                details={"import_job_id": str(dto.import_job_id)},
            ) from e

        try:
            job.mark_succeeded(summary, datetime.now(timezone.utc))
        except (InvalidJobStateError, InvalidDomainValueError) as e:
            raise OpsConflictError(str(e)) from e

        self._repo.save(job)
        return RunImportPipelineOutputDTO(
            import_job_id=job.import_job_id,
            status=job.status.value,
            result_summary=job.result_summary,
        )
