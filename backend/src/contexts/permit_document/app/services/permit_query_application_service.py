"""
Permit 查詢面用例服務（UC-PERMIT-03）。

責任：
- 經 **AuthorizationPort** 驗證存取權；
- 讀取 **PermitsRepository** / **DocumentsRepository**；
- 下載 URL 經 **ObjectStoragePort** 簽發；
- 回傳 **DTO**，不洩漏 ORM 型別至 API 邊界外（由 Controller 再包一層亦可）。
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.contexts.permit_document.app.dtos.permit_query_dtos import (
    CreateDocumentDownloadUrlInputDTO,
    CreateDocumentDownloadUrlOutputDTO,
    GetPermitByApplicationQueryDTO,
    GetPermitByIdQueryDTO,
    ListPermitDocumentsOutputDTO,
    ListPermitDocumentsQueryDTO,
    PermitCertificateSummaryDTO,
    PermitSummaryDTO,
    RequestPermitDocumentDownloadByApplicationDTO,
)
from src.contexts.permit_document.app.errors import PermitNotFoundAppError, PermitValidationAppError
from src.contexts.permit_document.domain.entities.permit_document import PENDING_FILE_ID_PLACEHOLDER
from src.contexts.permit_document.domain.value_objects.permit_status import PermitDocumentRecordStatusPhase
from src.contexts.permit_document.app.services.permit_mappers import (
    orm_documents_to_row_dto,
    orm_permits_to_summary_dto,
)
from src.contexts.permit_document.app.services.permit_service_context import PermitServiceContext
from src.contexts.permit_document.app.services.permit_status_api_mapping import (
    certificate_status_to_api,
    permit_status_to_api,
)
from src.contexts.permit_document.infra.schema.certificate_access_logs import CertificateAccessLogs
from src.contexts.permit_document.infra.schema.documents import Documents
from src.contexts.permit_document.infra.permit_local_storage import permit_certificate_pdf_path
from src.contexts.permit_document.app.services.permit_route_sync import sync_permit_route_from_latest_plan


class PermitQueryApplicationService:
    """Permit_Document 查詢用例實作。"""

    def __init__(self, ctx: PermitServiceContext) -> None:
        self._c = ctx

    def _certificate_summary(self, permit_id: UUID) -> PermitCertificateSummaryDTO | None:
        doc = self._c.documents.get_latest_by_permit_id(permit_id)
        if doc is None:
            return None
        api_status = certificate_status_to_api(doc.status)
        downloadable = (
            doc.status == PermitDocumentRecordStatusPhase.ACTIVE.value
            and doc.file_id != PENDING_FILE_ID_PLACEHOLDER
        )
        return PermitCertificateSummaryDTO(
            document_id=doc.document_id,
            version_no=doc.version_no,
            status=api_status,
            generated_at=doc.generated_at,
            downloadable=downloadable,
        )

    def _to_summary_dto(self, row) -> PermitSummaryDTO:
        base = orm_permits_to_summary_dto(row, certificate=self._certificate_summary(row.permit_id))
        return replace(base, status=permit_status_to_api(row.status))

    def _ensure_pending_certificate_document_and_job_if_absent(self, permit_id: UUID) -> None:
        """
        許可列存在但尚無 **documents** 列時（舊資料或未走完核發寫入），補齊與
        **create_permit_after_application_approved** 相同之 pending 文件列與（若尚無）pending job，
        以便後續同步產檔。
        """
        if self._c.documents.get_latest_by_permit_id(permit_id) is not None:
            return
        permit_row = self._c.permits.get_by_id(permit_id)
        if permit_row is None:
            return

        from src.contexts.permit_document.app.services.permit_mappers import domain_document_job_to_orm_row
        from src.contexts.permit_document.domain import DocumentGenerationJob, DocumentJobType, DocumentJobTypePhase
        from src.contexts.permit_document.domain.value_objects.document_type_code import DocumentTypeCodePhase

        now = datetime.now(timezone.utc)
        application_id = permit_row.application_id
        pending_jobs = [
            j for j in self._c.jobs.list_by_permit_id(permit_id) if j.status == "pending"
        ]
        if not pending_jobs:
            job = DocumentGenerationJob.enqueue(
                job_id=uuid4(),
                application_id=application_id,
                permit_id=permit_id,
                job_type=DocumentJobType(DocumentJobTypePhase.GENERATE_PERMIT_BUNDLE.value),
                now=now,
            )
            self._c.jobs.add(domain_document_job_to_orm_row(job))

        self._c.documents.add(
            Documents(
                document_id=uuid4(),
                permit_id=permit_id,
                application_id=application_id,
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

    def _sync_generate_certificate_if_latest_pending(self, permit_id: UUID) -> None:
        """
        申請人下載前：若最新憑證列仍為 **pending** 且存在對應 **pending** job，於此請求內同步產檔。

        已 **active** 或無待處理 job 則不做事（由後續校驗決定是否可下載）。
        """
        self._ensure_pending_certificate_document_and_job_if_absent(permit_id)
        latest = self._c.documents.get_latest_by_permit_id(permit_id)
        if latest is None:
            return
        if latest.status != PermitDocumentRecordStatusPhase.PENDING.value:
            return
        from src.contexts.permit_document.app.services.certificate_generation_application_service import (
            CertificateGenerationApplicationService,
        )

        svc = CertificateGenerationApplicationService(self._c)
        result = svc.process_pending_job_for_permit(permit_id)
        if result == "error":
            raise PermitValidationAppError(
                "使用證產製失敗，請稍後再試或聯繫承辦。",
                {"permit_id": str(permit_id)},
            )
        if result == "empty":
            raise PermitValidationAppError(
                "通行證文件尚無法下載（無產檔工作），請稍後再試或聯繫承辦。",
                {"permit_id": str(permit_id)},
            )

    def get_permit_by_application(self, q: GetPermitByApplicationQueryDTO) -> PermitSummaryDTO:
        """申請人視角：依 **application_id** 取得單一許可摘要。"""
        self._c.auth.assert_may_access_application(
            actor_user_id=q.actor_user_id,
            application_id=q.application_id,
        )
        row = self._c.permits.get_by_application_id(q.application_id)
        if row is None:
            raise PermitNotFoundAppError(
                "此申請尚無許可證",
                {"application_id": str(q.application_id)},
            )
        return self._to_summary_dto(row)

    def get_permit_by_id(self, q: GetPermitByIdQueryDTO) -> PermitSummaryDTO:
        """依 **permit_id** 取得許可摘要。"""
        self._c.auth.assert_may_access_permit(actor_user_id=q.actor_user_id, permit_id=q.permit_id)
        row = self._c.permits.get_by_id(q.permit_id)
        if row is None:
            raise PermitNotFoundAppError("許可證不存在", {"permit_id": str(q.permit_id)})
        return self._to_summary_dto(row)

    def list_documents(self, q: ListPermitDocumentsQueryDTO) -> ListPermitDocumentsOutputDTO:
        """列出許可底下之文件版本列。"""
        self._c.auth.assert_may_access_permit(actor_user_id=q.actor_user_id, permit_id=q.permit_id)
        permit_row = self._c.permits.get_by_id(q.permit_id)
        if permit_row is None:
            raise PermitNotFoundAppError("許可證不存在", {"permit_id": str(q.permit_id)})
        rows = self._c.documents.list_by_permit_id(q.permit_id)
        return ListPermitDocumentsOutputDTO(
            permit_id=q.permit_id,
            documents=[orm_documents_to_row_dto(r) for r in rows],
        )

    def create_document_download_url(
        self,
        inp: CreateDocumentDownloadUrlInputDTO,
    ) -> CreateDocumentDownloadUrlOutputDTO:
        """產生單一文件之短期下載 URL。"""
        self._c.auth.assert_may_access_permit(actor_user_id=inp.actor_user_id, permit_id=inp.permit_id)
        permit_row = self._c.permits.get_by_id(inp.permit_id)
        if permit_row is None:
            raise PermitNotFoundAppError("許可證不存在", {"permit_id": str(inp.permit_id)})
        synced_route = sync_permit_route_from_latest_plan(inp.permit_id)
        if synced_route:
            permit_row = self._c.permits.get_by_id(inp.permit_id)
            if permit_row is None:
                raise PermitNotFoundAppError("許可證不存在", {"permit_id": str(inp.permit_id)})

        doc = self._c.documents.get_by_id(inp.document_id)
        if doc is None or doc.permit_id != inp.permit_id:
            raise PermitNotFoundAppError(
                "文件不存在或不屬於該許可",
                {"permit_id": str(inp.permit_id), "document_id": str(inp.document_id)},
            )
        latest = self._c.documents.get_latest_by_permit_id(inp.permit_id)
        if latest is None or latest.document_id != doc.document_id:
            raise PermitValidationAppError(
                "僅能下載最新版本使用證",
                {
                    "permit_id": str(inp.permit_id),
                    "document_id": str(inp.document_id),
                },
            )
        if doc.file_id == PENDING_FILE_ID_PLACEHOLDER or doc.status == PermitDocumentRecordStatusPhase.PENDING.value:
            raise PermitValidationAppError(
                "此文件尚在產製中，請待產檔完成後再下載",
                {
                    "permit_id": str(inp.permit_id),
                    "document_id": str(inp.document_id),
                    "status": doc.status,
                },
            )
        if doc.status == PermitDocumentRecordStatusPhase.FAILED.value:
            raise PermitValidationAppError(
                "此文件產製失敗，請聯繫承辦或待系統重產後再試",
                {
                    "permit_id": str(inp.permit_id),
                    "document_id": str(inp.document_id),
                    "status": doc.status,
                },
            )
        if doc.status != PermitDocumentRecordStatusPhase.ACTIVE.value:
            raise PermitValidationAppError(
                "此文件狀態不允許下載",
                {"permit_id": str(inp.permit_id), "document_id": str(inp.document_id), "status": doc.status},
            )

        # 路線摘要已寫回 DB 時，若本機仍留舊 PDF，GET 簽章連結會直接回傳快取而不重繪；先刪檔強制重產。
        if synced_route and doc.file_id != PENDING_FILE_ID_PLACEHOLDER:
            permit_certificate_pdf_path(doc.file_id).unlink(missing_ok=True)

        self._c.certificate_access_logs.add(
            CertificateAccessLogs(
                access_log_id=uuid4(),
                document_id=doc.document_id,
                permit_id=inp.permit_id,
                accessed_by=inp.actor_user_id,
                access_type="download",
                client_ip=None,
            )
        )

        url, exp = self._c.storage.create_temporary_download_url(file_id=doc.file_id)
        file_name = f"{permit_row.permit_no}_v{doc.version_no}.pdf"
        return CreateDocumentDownloadUrlOutputDTO(download_url=url, expires_at=exp, file_name=file_name)

    def _default_download_document_id(self, permit_id: UUID) -> UUID:
        """
        未指定 document_id 時，選定一筆可下載文件列。

        責任：僅選 **active**（已寫入 storage 之檔案）；若僅有 **pending**（產檔中）則拋 **400** 說明原因，
        避免誤用佔位 **file_id** 簽 URL。
        """
        latest = self._c.documents.get_latest_by_permit_id(permit_id)
        if latest is None:
            raise PermitNotFoundAppError(
                "此許可尚無任何文件紀錄",
                {"permit_id": str(permit_id)},
            )
        if latest.status == PermitDocumentRecordStatusPhase.ACTIVE.value and latest.file_id != PENDING_FILE_ID_PLACEHOLDER:
            return latest.document_id

        if latest.status in (
            PermitDocumentRecordStatusPhase.PENDING.value,
            PermitDocumentRecordStatusPhase.FAILED.value,
        ):
            raise PermitValidationAppError(
                "通行證文件產製中，產檔完成後即可下載，請稍後再試",
                {"permit_id": str(permit_id), "document_status": latest.status},
            )

        raise PermitNotFoundAppError(
            "尚無可下載之許可文件",
            {"permit_id": str(permit_id)},
        )

    def create_document_download_url_by_application(
        self,
        inp: RequestPermitDocumentDownloadByApplicationDTO,
    ) -> CreateDocumentDownloadUrlOutputDTO:
        """
        依 **application_id** 定位許可後，產生指定 **document_id** 之短期下載 URL。

        責任：供申請人 API（路徑僅帶申請識別）組合；授權與文件歸屬校驗沿用既有方法。
        **document_id** 省略時由 **_default_download_document_id** 決定預設文件。
        """
        summary = self.get_permit_by_application(
            GetPermitByApplicationQueryDTO(
                application_id=inp.application_id,
                actor_user_id=inp.actor_user_id,
            )
        )
        self._sync_generate_certificate_if_latest_pending(summary.permit_id)
        doc_id = inp.document_id
        if doc_id is None:
            doc_id = self._default_download_document_id(summary.permit_id)
        return self.create_document_download_url(
            CreateDocumentDownloadUrlInputDTO(
                permit_id=summary.permit_id,
                document_id=doc_id,
                actor_user_id=inp.actor_user_id,
            )
        )
