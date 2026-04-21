"""
Permit 命令面用例服務（UC-PERMIT-01、重產請求、工作單完成等）。

責任：
- 呼叫 **IssuanceContextReader** 取得跨 context 前置資料；
- 以領域工廠 **Permit.create_for_approved_application** 與 **DocumentGenerationJob.enqueue** 建立聚合與工作；
- 經 **permit_mappers** 寫入 Infra Repository；
- 領域例外經 **raise_permit_domain_as_app** 轉譯。

交易說明：
- 與既有專案一致：各 `Repository.add` 內部各自 `get_session()` 提交；**許可列與工作列非單一 DB transaction**。
  若需原子性，後續應於 Infra 提供單一 Session 之工作單元或 stored procedure。
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.contexts.permit_document.domain.entities.permit_document import PENDING_FILE_ID_PLACEHOLDER
from src.contexts.permit_document.domain.value_objects.document_type_code import DocumentTypeCodePhase
from src.contexts.permit_document.infra.schema.documents import Documents

from src.contexts.permit_document.app.dtos.permit_command_dtos import (
    CreatePermitInputDTO,
    CreatePermitOutputDTO,
    RecordDocumentJobCompletedInputDTO,
    RequestDocumentRegenerationInputDTO,
    RequestDocumentRegenerationOutputDTO,
)
from src.contexts.permit_document.app.errors import (
    PermitConflictAppError,
    PermitNotFoundAppError,
    PermitValidationAppError,
    raise_permit_domain_as_app,
)
from src.contexts.permit_document.app.services.integrations import (
    build_permit_no_from_application,
    build_route_summary_text_for_plan,
)
from src.contexts.permit_document.app.services.permit_mappers import (
    domain_document_job_to_orm_row,
    domain_permit_to_orm_row,
)
from src.contexts.permit_document.app.services.permit_service_context import PermitServiceContext
from src.contexts.permit_document.domain import (
    DocumentGenerationJob,
    DocumentJobType,
    DocumentJobTypePhase,
    FinalRouteBinding,
    Permit,
    PermitApprovedPeriod,
    PermitNo,
    PermitStatusPhase,
    RouteSummaryText,
)
from src.contexts.permit_document.domain.entities.permit_document import PENDING_FILE_ID_PLACEHOLDER
from src.contexts.permit_document.domain.value_objects.document_type_code import DocumentTypeCodePhase
from src.contexts.permit_document.infra.schema.documents import Documents


class PermitCommandApplicationService:
    """Permit_Document 命令用例實作。"""

    def __init__(self, ctx: PermitServiceContext) -> None:
        self._c = ctx

    # ------------------------------------------------------------------ UC-PERMIT-01
    def create_permit_after_application_approved(self, inp: CreatePermitInputDTO) -> CreatePermitOutputDTO:
        """
        於申請 **已核准** 且路線已選定候選後，建立許可與首筆產檔工作。

        責任：重複申請（已存在許可）回 **409**；未核准或無候選回 **400**。
        """
        snap = self._c.issuance.load(inp.application_id)
        if not snap.application_approved:
            raise PermitValidationAppError(
                "僅核准後之申請可建立許可證",
                {"application_id": str(inp.application_id), "status": "not_approved"},
            )

        existing = self._c.permits.get_by_application_id(inp.application_id)
        if existing is not None:
            raise PermitConflictAppError(
                "此申請已建立許可證",
                {"application_id": str(inp.application_id), "permit_id": str(existing.permit_id)},
            )

        route_summary = RouteSummaryText(
            build_route_summary_text_for_plan(
                inp.application_id,
                snap.selected_candidate_id,
                override_id=snap.override_id,
            )
        )
        permit_no = PermitNo(build_permit_no_from_application(snap.application_no))
        binding = raise_permit_domain_as_app(
            lambda: FinalRouteBinding(
                selected_candidate_id=snap.selected_candidate_id,
                override_id=snap.override_id,
            )
        )
        period = raise_permit_domain_as_app(
            lambda: PermitApprovedPeriod(start_at=snap.approved_start_at, end_at=snap.approved_end_at)
        )
        now = datetime.now(timezone.utc)
        permit_id = uuid4()

        permit = raise_permit_domain_as_app(
            lambda: Permit.create_for_approved_application(
                permit_id=permit_id,
                permit_no=permit_no,
                application_id=inp.application_id,
                application_approved=True,
                approved_period=period,
                route_binding=binding,
                route_summary=route_summary,
                note=inp.note,
                now=now,
            )
        )

        permit_row = domain_permit_to_orm_row(permit, note=inp.note)
        self._c.permits.add(permit_row)

        job = DocumentGenerationJob.enqueue(
            job_id=uuid4(),
            application_id=inp.application_id,
            permit_id=permit_id,
            job_type=DocumentJobType(DocumentJobTypePhase.GENERATE_PERMIT_BUNDLE.value),
            now=now,
        )
        job_row = domain_document_job_to_orm_row(job)
        self._c.jobs.add(job_row)

        self._c.documents.add(
            Documents(
                document_id=uuid4(),
                permit_id=permit_id,
                application_id=inp.application_id,
                document_type=DocumentTypeCodePhase.PERMIT_CERTIFICATE_PDF.value,
                file_id=PENDING_FILE_ID_PLACEHOLDER,
                template_code="ntpc_heavy_truck_temp_v1",
                version_no=1,
                status="pending",
                is_latest=True,
                checksum_sha256=None,
                generated_at=None,
                error_message=None,
                created_at=now,
                updated_at=now,
            )
        )

        return CreatePermitOutputDTO(
            permit_id=permit.permit_id,
            permit_no=permit.permit_no.value,
            application_id=permit.application_id,
            status=permit.status.value,
            document_job_id=job.job_id,
        )

    # ------------------------------------------------------------------ 重產文件
    def request_document_regeneration(
        self,
        inp: RequestDocumentRegenerationInputDTO,
    ) -> RequestDocumentRegenerationOutputDTO:
        """
        標示待補產並排入新產檔工作（初版：以 ORM 狀態欄位更新為主）。

        責任：申請人須通過 **AuthorizationPort**；僅 **issued** 之許可轉 **issued_pending_document_regen**。
        """
        self._c.auth.assert_may_access_application(
            actor_user_id=inp.actor_user_id,
            application_id=inp.application_id,
        )
        row = self._c.permits.get_by_application_id(inp.application_id)
        if row is None:
            raise PermitNotFoundAppError("此申請尚無許可證", {"application_id": str(inp.application_id)})

        if row.status == PermitStatusPhase.ISSUED.value:
            row.status = PermitStatusPhase.ISSUED_WITH_PENDING_DOCUMENT_REGEN.value
            row.updated_at = datetime.now(timezone.utc)
            self._c.permits.merge_update(row)
        elif row.status == PermitStatusPhase.ISSUED_WITH_PENDING_DOCUMENT_REGEN.value:
            pass
        elif row.status == PermitStatusPhase.PENDING_GENERATION.value:
            pass
        elif row.status == PermitStatusPhase.GENERATION_FAILED.value:
            row.status = PermitStatusPhase.PENDING_GENERATION.value
            row.updated_at = datetime.now(timezone.utc)
            self._c.permits.merge_update(row)
        else:
            raise PermitConflictAppError(
                "目前許可狀態不允許請求重產",
                {"permit_id": str(row.permit_id), "status": row.status},
            )

        now = datetime.now(timezone.utc)
        latest = self._c.documents.get_latest_by_permit_id(row.permit_id)
        if latest is not None:
            self._c.documents.merge_update(
                Documents(
                    document_id=latest.document_id,
                    permit_id=latest.permit_id,
                    application_id=latest.application_id,
                    document_type=latest.document_type,
                    file_id=latest.file_id,
                    template_code=latest.template_code,
                    version_no=latest.version_no,
                    status=latest.status,
                    is_latest=False,
                    checksum_sha256=latest.checksum_sha256,
                    generated_at=latest.generated_at,
                    error_message=latest.error_message,
                    created_at=latest.created_at,
                    updated_at=now,
                )
            )
            next_ver = latest.version_no + 1
            doc_type = latest.document_type
            tmpl = latest.template_code
        else:
            next_ver = 1
            doc_type = DocumentTypeCodePhase.PERMIT_CERTIFICATE_PDF.value
            tmpl = "ntpc_heavy_truck_temp_v1"

        self._c.documents.add(
            Documents(
                document_id=uuid4(),
                permit_id=row.permit_id,
                application_id=inp.application_id,
                document_type=doc_type,
                file_id=PENDING_FILE_ID_PLACEHOLDER,
                template_code=tmpl,
                version_no=next_ver,
                status="pending",
                is_latest=True,
                checksum_sha256=None,
                generated_at=None,
                error_message=None,
                created_at=now,
                updated_at=now,
            )
        )

        job = DocumentGenerationJob.enqueue(
            job_id=uuid4(),
            application_id=inp.application_id,
            permit_id=row.permit_id,
            job_type=DocumentJobType(DocumentJobTypePhase.GENERATE_PERMIT_BUNDLE.value),
            now=now,
        )
        self._c.jobs.add(domain_document_job_to_orm_row(job))

        refreshed = self._c.permits.get_by_id(row.permit_id)
        assert refreshed is not None
        return RequestDocumentRegenerationOutputDTO(
            permit_id=refreshed.permit_id,
            new_document_job_id=job.job_id,
            permit_status=refreshed.status,
        )

    # ------------------------------------------------------------------ UC-PERMIT-02 後段（工作完成）
    def mark_document_job_completed(self, inp: RecordDocumentJobCompletedInputDTO) -> None:
        """將工作單標記為 **completed**（由 worker 呼叫；預期目前狀態為 **processing**）。"""
        from src.contexts.permit_document.domain.entities.document_job import (
            DocumentGenerationJob as JobEntity,
        )
        from src.contexts.permit_document.domain.value_objects import (
            DocumentJobStatus,
            DocumentJobType,
        )

        row = self._c.jobs.get_by_id(inp.job_id)
        if row is None:
            raise PermitNotFoundAppError("工作單不存在", {"job_id": str(inp.job_id)})
        if row.status == "completed":
            return
        if row.status != "processing":
            raise PermitConflictAppError(
                "工作單狀態不允許標記完成",
                {"job_id": str(inp.job_id), "status": row.status},
            )

        dj = JobEntity(
            job_id=row.job_id,
            application_id=row.application_id,
            permit_id=row.permit_id,
            job_type=DocumentJobType(row.job_type),
            status=DocumentJobStatus(row.status),
            error_message=row.error_message,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
        dj.mark_completed(inp.completed_at)
        self._c.jobs.merge_update(domain_document_job_to_orm_row(dj))
