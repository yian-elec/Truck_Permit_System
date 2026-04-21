"""
OpsReadPort 實作 — 使用 get_session() 與 ORM 模型組裝讀取 DTO。

責任：支援 Application 層 OpsQueryApplicationService；不內含業務規則，僅查詢與映射。
"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional
from uuid import UUID

from shared.core.db.connection import get_session

from src.contexts.integration_operations.app.dtos import (
    AuditLogListItemDTO,
    ImportJobDetailDTO,
    ImportJobListItemDTO,
    NotificationJobListItemDTO,
    OcrJobDetailDTO,
    OcrJobListItemDTO,
    OcrResultItemDTO,
)
from src.contexts.integration_operations.infra.schema import (
    AuditLogs,
    ImportJobs,
    NotificationJobs,
    OcrJobs,
    OcrResults,
)


def _num_to_float(v: Decimal | float | None) -> float | None:
    if v is None:
        return None
    if isinstance(v, Decimal):
        return float(v)
    return float(v)


class OpsReadRepositoryImpl:
    """Ops 唯讀查詢（實作 OpsReadPort 結構方法，供型別檢查／依賴注入）。"""

    def list_ocr_jobs(self, *, limit: int, offset: int) -> list[OcrJobListItemDTO]:
        with get_session() as session:
            rows = (
                session.query(OcrJobs)
                .order_by(OcrJobs.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
            return [_ocr_job_row_to_list_item(r) for r in rows]

    def get_ocr_job_detail(self, ocr_job_id: UUID) -> Optional[OcrJobDetailDTO]:
        with get_session() as session:
            job_row = session.query(OcrJobs).filter(OcrJobs.ocr_job_id == ocr_job_id).first()
            if job_row is None:
                return None
            res_rows = (
                session.query(OcrResults)
                .filter(OcrResults.attachment_id == job_row.attachment_id)
                .order_by(OcrResults.created_at)
                .all()
            )
            results = [_ocr_result_row_to_item(r) for r in res_rows]
            return OcrJobDetailDTO(job=_ocr_job_row_to_list_item(job_row), results=results)

    def list_notification_jobs(self, *, limit: int, offset: int) -> list[NotificationJobListItemDTO]:
        with get_session() as session:
            rows = (
                session.query(NotificationJobs)
                .order_by(NotificationJobs.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
            return [
                NotificationJobListItemDTO(
                    notification_job_id=r.notification_job_id,
                    channel=r.channel,
                    recipient=r.recipient,
                    template_code=r.template_code,
                    status=r.status,
                    sent_at=r.sent_at,
                    error_message=r.error_message,
                    created_at=r.created_at,
                    updated_at=r.updated_at,
                )
                for r in rows
            ]

    def list_import_jobs(self, *, limit: int, offset: int) -> list[ImportJobListItemDTO]:
        with get_session() as session:
            rows = (
                session.query(ImportJobs)
                .order_by(ImportJobs.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
            return [_import_row_to_list_item(r) for r in rows]

    def get_import_job_detail(self, import_job_id: UUID) -> Optional[ImportJobDetailDTO]:
        with get_session() as session:
            r = session.query(ImportJobs).filter(ImportJobs.import_job_id == import_job_id).first()
            if r is None:
                return None
            return ImportJobDetailDTO(job=_import_row_to_list_item(r))

    def list_audit_logs(self, *, limit: int, offset: int) -> list[AuditLogListItemDTO]:
        with get_session() as session:
            rows = (
                session.query(AuditLogs)
                .order_by(AuditLogs.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
            return [_audit_row_to_item(r) for r in rows]


def _ocr_job_row_to_list_item(r: OcrJobs) -> OcrJobListItemDTO:
    return OcrJobListItemDTO(
        ocr_job_id=r.ocr_job_id,
        attachment_id=r.attachment_id,
        provider_code=r.provider_code,
        status=r.status,
        started_at=r.started_at,
        finished_at=r.finished_at,
        error_message=r.error_message,
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


def _ocr_result_row_to_item(r: OcrResults) -> OcrResultItemDTO:
    raw = dict(r.raw_json) if r.raw_json is not None else None
    return OcrResultItemDTO(
        ocr_result_id=r.ocr_result_id,
        attachment_id=r.attachment_id,
        field_name=r.field_name,
        field_value=r.field_value,
        confidence=_num_to_float(r.confidence),
        raw_json=raw,
        created_at=r.created_at,
    )


def _import_row_to_list_item(r: ImportJobs) -> ImportJobListItemDTO:
    return ImportJobListItemDTO(
        import_job_id=r.import_job_id,
        job_type=r.job_type,
        source_name=r.source_name,
        source_ref=r.source_ref,
        status=r.status,
        started_at=r.started_at,
        finished_at=r.finished_at,
        result_summary=r.result_summary,
        error_message=r.error_message,
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


def _audit_row_to_item(r: AuditLogs) -> AuditLogListItemDTO:
    ip = str(r.client_ip) if r.client_ip is not None else None
    before = r.before_json
    after = r.after_json
    return AuditLogListItemDTO(
        audit_log_id=r.audit_log_id,
        actor_user_id=r.actor_user_id,
        actor_type=r.actor_type,
        action_code=r.action_code,
        resource_type=r.resource_type,
        resource_id=r.resource_id,
        before_json=before,
        after_json=after,
        client_ip=ip,
        created_at=r.created_at,
    )
