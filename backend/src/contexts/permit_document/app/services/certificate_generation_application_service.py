"""
UC-PERMIT-02：撿取待處理產檔工作、產生使用證 PDF、寫入 ops.stored_files、更新 permit／documents／job。

責任：供 worker／CLI 呼叫；與 HTTP 解耦。
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from uuid import UUID, uuid4

from shared.core.logger.logger import logger

from src.contexts.application.infra.repositories.application_repository_impl import (
    ApplicationRepositoryImpl,
)
from src.contexts.application.infra.schema.stored_files import StoredFiles
from src.contexts.permit_document.app.errors import PermitCertificateFontError
from src.contexts.permit_document.app.services.integrations.permit_certificate_pdf_render import (
    PermitCertificateLayoutInput,
    render_permit_certificate_pdf,
)
from src.contexts.permit_document.app.services.permit_mappers import domain_document_job_to_orm_row
from src.contexts.permit_document.app.services.permit_service_context import PermitServiceContext
from src.contexts.permit_document.domain.entities.document_job import DocumentGenerationJob
from src.contexts.permit_document.domain.value_objects import DocumentJobStatus, DocumentJobType
from src.contexts.permit_document.infra.schema.documents import Documents
from src.contexts.permit_document.infra.schema.document_jobs import DocumentJobs
from src.contexts.permit_document.infra.schema.permits import Permits

from src.contexts.permit_document.app.services.permit_route_sync import sync_permit_route_from_latest_plan


def _primary_vehicle_plate(application_id: UUID, apps: ApplicationRepositoryImpl) -> str:
    app = apps.get_by_id(application_id)
    if app is None or not app.vehicles:
        return "（未登記車號）"
    primary = next((v for v in app.vehicles if v.is_primary), app.vehicles[0])
    return primary.plate_no.value


class CertificateGenerationApplicationService:
    """產檔工作處理（單次 job 完整寫入）。"""

    def __init__(
        self,
        ctx: PermitServiceContext,
        *,
        applications: ApplicationRepositoryImpl | None = None,
    ) -> None:
        self._c = ctx
        self._apps = applications or ApplicationRepositoryImpl()

    def process_next_pending_job(self) -> str:
        """
        處理一筆 **pending** 工作。

        Returns:
            ``"processed"`` | ``"empty"`` | ``"error"``
        """
        rows = self._c.jobs.list_pending(limit=1)
        if not rows:
            return "empty"
        return self._run_pipeline_for_job_row(rows[0])

    def process_pending_job_for_permit(self, permit_id: UUID) -> str:
        """
        處理指定許可底下之一筆 **pending** 工作（供下載前同步產檔）。

        Returns:
            ``"processed"`` | ``"empty"`` | ``"error"``
        """
        rows = [j for j in self._c.jobs.list_by_permit_id(permit_id) if j.status == "pending"]
        if not rows:
            return "empty"
        job_row = min(rows, key=lambda j: j.created_at)
        return self._run_pipeline_for_job_row(job_row)

    def ensure_local_permit_pdf_file(self, file_id: UUID) -> bool:
        """
        磁碟無 PDF 但 DB 已有 **active** 文件列時，依許可重畫並寫入（目錄清空／換機後自癒）。
        """
        from src.contexts.permit_document.infra.permit_local_storage import permit_certificate_pdf_path

        path = permit_certificate_pdf_path(file_id)
        if path.is_file():
            return True

        doc = self._c.documents.get_by_file_id(file_id)
        if doc is None or doc.status != "active":
            return False

        permit_orm = self._c.permits.get_by_id(doc.permit_id)
        if permit_orm is None:
            return False

        now = datetime.now(timezone.utc)
        plate = _primary_vehicle_plate(doc.application_id, self._apps)
        layout = PermitCertificateLayoutInput(
            permit_no=permit_orm.permit_no,
            vehicle_plate=plate,
            route_summary_text=permit_orm.route_summary_text,
            approved_start_at=permit_orm.approved_start_at,
            approved_end_at=permit_orm.approved_end_at,
        )
        try:
            pdf_bytes = render_permit_certificate_pdf(layout)
        except PermitCertificateFontError:
            logger.infra_error(
                "ensure_local_permit_pdf_file: CJK font or PDF validation failed; file not written",
                file_id=str(file_id),
            )
            return False
        sha = hashlib.sha256(pdf_bytes).hexdigest()
        self._persist_stored_file(file_id=file_id, pdf_bytes=pdf_bytes, sha256_hex=sha, now=now)

        if doc.checksum_sha256 != sha:
            self._c.documents.merge_update(
                Documents(
                    document_id=doc.document_id,
                    permit_id=doc.permit_id,
                    application_id=doc.application_id,
                    document_type=doc.document_type,
                    file_id=doc.file_id,
                    template_code=doc.template_code,
                    version_no=doc.version_no,
                    status=doc.status,
                    is_latest=doc.is_latest,
                    checksum_sha256=sha,
                    generated_at=doc.generated_at,
                    error_message=doc.error_message,
                    created_at=doc.created_at,
                    updated_at=now,
                )
            )

        return path.is_file()

    def _run_pipeline_for_job_row(self, job_row: DocumentJobs) -> str:
        now = datetime.now(timezone.utc)
        permit_id = job_row.permit_id
        application_id = job_row.application_id
        if permit_id is None:
            self._set_job_failed(job_row, "permit_id is null on job", now)
            return "error"

        permit_orm = self._c.permits.get_by_id(permit_id)
        if permit_orm is None:
            self._set_job_failed(job_row, "permit not found", now)
            return "error"

        sync_permit_route_from_latest_plan(permit_id)
        permit_orm = self._c.permits.get_by_id(permit_id)
        if permit_orm is None:
            self._set_job_failed(job_row, "permit not found after route sync", now)
            return "error"

        doc = self._c.documents.get_latest_by_permit_id(permit_id)
        if doc is None:
            self._set_job_failed(job_row, "no certificate document row", now)
            return "error"

        dj = DocumentGenerationJob(
            job_id=job_row.job_id,
            application_id=job_row.application_id,
            permit_id=job_row.permit_id,
            job_type=DocumentJobType(job_row.job_type),
            status=DocumentJobStatus(job_row.status),
            error_message=job_row.error_message,
            created_at=job_row.created_at,
            updated_at=job_row.updated_at,
        )
        try:
            dj.mark_processing(now)
        except Exception:
            self._set_job_failed(job_row, "job not in pending state", now)
            return "error"

        proc_row = domain_document_job_to_orm_row(dj, started_at=now)
        self._c.jobs.merge_update(proc_row)

        try:
            plate = _primary_vehicle_plate(application_id, self._apps)
            layout = PermitCertificateLayoutInput(
                permit_no=permit_orm.permit_no,
                vehicle_plate=plate,
                route_summary_text=permit_orm.route_summary_text,
                approved_start_at=permit_orm.approved_start_at,
                approved_end_at=permit_orm.approved_end_at,
            )
            pdf_bytes = render_permit_certificate_pdf(layout)
            sha = hashlib.sha256(pdf_bytes).hexdigest()
            file_id = uuid4()
            self._persist_stored_file(file_id=file_id, pdf_bytes=pdf_bytes, sha256_hex=sha, now=now)

            doc_update = Documents(
                document_id=doc.document_id,
                permit_id=doc.permit_id,
                application_id=doc.application_id,
                document_type=doc.document_type,
                file_id=file_id,
                template_code=doc.template_code,
                version_no=doc.version_no,
                status="active",
                is_latest=doc.is_latest,
                checksum_sha256=sha,
                generated_at=now,
                error_message=None,
                created_at=doc.created_at,
                updated_at=now,
            )
            self._c.documents.merge_update(doc_update)

            p_up = Permits(
                permit_id=permit_orm.permit_id,
                permit_no=permit_orm.permit_no,
                application_id=permit_orm.application_id,
                status="issued",
                approved_start_at=permit_orm.approved_start_at,
                approved_end_at=permit_orm.approved_end_at,
                selected_candidate_id=permit_orm.selected_candidate_id,
                override_id=permit_orm.override_id,
                route_summary_text=permit_orm.route_summary_text,
                note=permit_orm.note,
                issued_at=now,
                issued_by=None,
                revoked_at=permit_orm.revoked_at,
                revoked_by=permit_orm.revoked_by,
                revoked_reason=permit_orm.revoked_reason,
                created_at=permit_orm.created_at,
                updated_at=now,
            )
            self._c.permits.merge_update(p_up)

            dj_done = DocumentGenerationJob(
                job_id=job_row.job_id,
                application_id=job_row.application_id,
                permit_id=job_row.permit_id,
                job_type=DocumentJobType(job_row.job_type),
                status=DocumentJobStatus("processing"),
                error_message=None,
                created_at=job_row.created_at,
                updated_at=now,
            )
            dj_done.mark_completed(now)
            done_row = domain_document_job_to_orm_row(
                dj_done,
                started_at=now,
                finished_at=now,
            )
            self._c.jobs.merge_update(done_row)
        except PermitCertificateFontError as exc:
            self._fail_after_processing(job_row, permit_orm, doc, exc.message, now)
            return "error"
        except Exception as exc:
            self._fail_after_processing(job_row, permit_orm, doc, str(exc), now)
            return "error"
        return "processed"

    def _persist_stored_file(
        self,
        *,
        file_id: UUID,
        pdf_bytes: bytes,
        sha256_hex: str,
        now: datetime,
    ) -> None:
        from shared.core.db.connection import get_session

        from src.contexts.permit_document.infra.permit_local_storage import (
            permit_certificate_files_directory,
        )

        root = permit_certificate_files_directory()
        root.mkdir(parents=True, exist_ok=True)
        path = root / f"{file_id}.pdf"
        path.write_bytes(pdf_bytes)

        with get_session() as session:
            session.merge(
                StoredFiles(
                    file_id=file_id,
                    bucket_name="permit-certificates",
                    object_key=f"permit/{file_id}.pdf",
                    storage_provider="local",
                    mime_type="application/pdf",
                    size_bytes=len(pdf_bytes),
                    checksum_sha256=sha256_hex,
                    virus_scan_status="skipped",
                    created_at=now,
                )
            )

    def _set_job_failed(self, job_row: DocumentJobs, message: str, now: datetime) -> None:
        fail = DocumentJobs(
            job_id=job_row.job_id,
            application_id=job_row.application_id,
            permit_id=job_row.permit_id,
            job_type=job_row.job_type,
            status="failed",
            error_message=message,
            triggered_by=job_row.triggered_by,
            trigger_source=job_row.trigger_source or "system",
            retry_count=job_row.retry_count or 0,
            payload_json=job_row.payload_json,
            started_at=job_row.started_at,
            finished_at=now,
            created_at=job_row.created_at,
            updated_at=now,
        )
        self._c.jobs.merge_update(fail)

    def _fail_after_processing(
        self,
        job_row: DocumentJobs,
        permit: Permits,
        doc: Documents,
        message: str,
        now: datetime,
    ) -> None:
        dj = DocumentGenerationJob(
            job_id=job_row.job_id,
            application_id=job_row.application_id,
            permit_id=job_row.permit_id,
            job_type=DocumentJobType(job_row.job_type),
            status=DocumentJobStatus("processing"),
            error_message=None,
            created_at=job_row.created_at,
            updated_at=now,
        )
        try:
            dj.mark_failed(message, now)
        except Exception:
            self._set_job_failed(job_row, message, now)
        else:
            self._c.jobs.merge_update(
                domain_document_job_to_orm_row(dj, started_at=job_row.started_at or now, finished_at=now)
            )

        p_up = Permits(
            permit_id=permit.permit_id,
            permit_no=permit.permit_no,
            application_id=permit.application_id,
            status="generation_failed",
            approved_start_at=permit.approved_start_at,
            approved_end_at=permit.approved_end_at,
            selected_candidate_id=permit.selected_candidate_id,
            override_id=permit.override_id,
            route_summary_text=permit.route_summary_text,
            note=permit.note,
            issued_at=permit.issued_at,
            issued_by=permit.issued_by,
            revoked_at=permit.revoked_at,
            revoked_by=permit.revoked_by,
            revoked_reason=permit.revoked_reason,
            created_at=permit.created_at,
            updated_at=now,
        )
        self._c.permits.merge_update(p_up)

        doc_fail = Documents(
            document_id=doc.document_id,
            permit_id=doc.permit_id,
            application_id=doc.application_id,
            document_type=doc.document_type,
            file_id=doc.file_id,
            template_code=doc.template_code,
            version_no=doc.version_no,
            status="failed",
            is_latest=doc.is_latest,
            checksum_sha256=doc.checksum_sha256,
            generated_at=doc.generated_at,
            error_message=message[:2000],
            created_at=doc.created_at,
            updated_at=now,
        )
        self._c.documents.merge_update(doc_fail)
