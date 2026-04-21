"""
UC-ROUTE-06：KML 匯入作業（與 ops.import_jobs 同步執行）。
"""

from __future__ import annotations

from uuid import UUID

from src.contexts.integration_operations.app.dtos import (
    RunImportPipelineInputDTO,
    ScheduleImportJobInputDTO,
)
from src.contexts.integration_operations.app.errors import OpsExternalDependencyError
from src.contexts.integration_operations.app.services.import_application_service import (
    ImportApplicationService,
)
from src.contexts.integration_operations.domain.repositories import ImportJobRepository
from src.contexts.integration_operations.infra.repositories import ImportJobRepositoryImpl
from src.contexts.routing_restriction.app.dtos.map_import_dtos import (
    MapImportJobStatusDTO,
    RequestKmlImportInputDTO,
)
from src.contexts.routing_restriction.app.errors import RoutingValidationAppError
from src.contexts.routing_restriction.infra.import_ingestion.kml_restrictions_ingestion import (
    INLINE_KML_PLACEHOLDER_REF,
    KML_RESTRICTIONS_JOB_TYPE,
    KmlRestrictionsImportIngestion,
    LONG_URL_PLACEHOLDER_REF,
)
from src.contexts.routing_restriction.infra.kml.import_context import push_kml_body, reset_kml_body

KML_SOURCE_NAME = "kml"


class MapImportApplicationService:
    """圖資匯入用例服務。"""

    def __init__(
        self,
        *,
        import_application_service: ImportApplicationService | None = None,
        import_job_repository: ImportJobRepository | None = None,
    ) -> None:
        self._import_repo = import_job_repository or ImportJobRepositoryImpl()
        ingestion = KmlRestrictionsImportIngestion()
        self._import_app = import_application_service or ImportApplicationService(
            self._import_repo,
            ingestion,
        )

    def request_kml_import(self, dto: RequestKmlImportInputDTO) -> MapImportJobStatusDTO:
        text = dto.source_description.strip()
        is_url = text.startswith(("http://", "https://"))
        # 超過 DB source_ref(255) 時經 ContextVar 傳完整字串（長網址或長 inline KML）；job 列只存佔位字串。
        use_ctx = len(text) > 255
        if use_ctx:
            ref = LONG_URL_PLACEHOLDER_REF if is_url else INLINE_KML_PLACEHOLDER_REF
            tok = push_kml_body(text)
        else:
            tok = None
            ref = text[:255]
        try:
            sched = self._import_app.schedule_import(
                ScheduleImportJobInputDTO(
                    job_type=KML_RESTRICTIONS_JOB_TYPE,
                    source_name=KML_SOURCE_NAME,
                    source_ref=ref,
                )
            )
            run = self._import_app.run_import_pipeline(
                RunImportPipelineInputDTO(import_job_id=sched.import_job_id)
            )
        except OpsExternalDependencyError as e:
            msg = str(e)
            if "import ingestion failed:" in msg:
                msg = msg.split("import ingestion failed:", 1)[-1].strip()
            raise RoutingValidationAppError(
                msg[:2000],
                details=getattr(e, "details", None),
            ) from e
        except ValueError as e:
            raise RoutingValidationAppError(str(e), details=None) from e
        finally:
            if tok is not None:
                reset_kml_body(tok)

        return MapImportJobStatusDTO(
            import_job_id=run.import_job_id,
            status=run.status,
            message=run.result_summary,
        )

    def get_import_job_status(self, import_job_id: str) -> MapImportJobStatusDTO | None:
        try:
            jid = UUID(import_job_id)
        except ValueError:
            return None
        job = self._import_repo.find_by_id(jid)
        if job is None:
            return None
        msg = job.result_summary or job.error_message
        return MapImportJobStatusDTO(
            import_job_id=job.import_job_id,
            status=job.status.value,
            message=msg,
        )
