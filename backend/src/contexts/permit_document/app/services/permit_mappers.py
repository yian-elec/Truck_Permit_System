"""
Permit 領域物件與 ORM 列之映射。

責任：單向由領域／值物件組出 **新增** 用之 SQLAlchemy 模型實例；不承擔查詢列還原領域聚合（可後續擴充）。
"""

from __future__ import annotations

from src.contexts.permit_document.domain.entities import DocumentGenerationJob, Permit
from src.contexts.permit_document.infra.schema.document_jobs import DocumentJobs
from src.contexts.permit_document.infra.schema.documents import Documents
from src.contexts.permit_document.infra.schema.permits import Permits


def domain_permit_to_orm_row(p: Permit, *, note: str | None) -> Permits:
    """將 **Permit** 聚合根映射為 `permit.permits` 新增列。"""
    return Permits(
        permit_id=p.permit_id,
        permit_no=p.permit_no.value,
        application_id=p.application_id,
        status=p.status.value,
        approved_start_at=p.approved_period.start_at,
        approved_end_at=p.approved_period.end_at,
        selected_candidate_id=p.route_binding.selected_candidate_id,
        override_id=p.route_binding.override_id,
        route_summary_text=p.route_summary.value,
        note=note,
        issued_at=p.issued_at,
        issued_by=None,
        revoked_at=None,
        revoked_by=None,
        revoked_reason=None,
    )


def domain_document_job_to_orm_row(
    job: DocumentGenerationJob,
    *,
    started_at: object | None = None,
    finished_at: object | None = None,
) -> DocumentJobs:
    """將 **DocumentGenerationJob** 映射為 `permit.document_jobs` 新增／更新列。"""
    return DocumentJobs(
        job_id=job.job_id,
        application_id=job.application_id,
        permit_id=job.permit_id,
        job_type=job.job_type.value,
        status=job.status.value,
        error_message=job.error_message,
        triggered_by=None,
        trigger_source="system",
        retry_count=0,
        payload_json=None,
        started_at=started_at,
        finished_at=finished_at,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


def orm_documents_to_row_dto(row: Documents) -> "PermitDocumentRowDTO":
    """ORM **Documents** → 查詢 DTO（延遲匯入避免循環）。"""
    from src.contexts.permit_document.app.dtos.permit_query_dtos import PermitDocumentRowDTO

    return PermitDocumentRowDTO(
        document_id=row.document_id,
        permit_id=row.permit_id,
        application_id=row.application_id,
        document_type=row.document_type,
        file_id=row.file_id,
        template_code=row.template_code,
        version_no=row.version_no,
        status=row.status,
    )


def orm_permits_to_summary_dto(row: Permits, *, certificate: "PermitCertificateSummaryDTO | None" = None) -> "PermitSummaryDTO":
    from src.contexts.permit_document.app.dtos.permit_query_dtos import PermitSummaryDTO

    return PermitSummaryDTO(
        permit_id=row.permit_id,
        permit_no=row.permit_no,
        application_id=row.application_id,
        status=row.status,
        approved_start_at=row.approved_start_at,
        approved_end_at=row.approved_end_at,
        route_summary_text=row.route_summary_text,
        issued_at=row.issued_at,
        certificate=certificate,
    )
