"""
Domain ↔ ORM 映射（僅供 infra repositories 使用）。

責任：將 ops.* 資料列轉回領域聚合／值物件，與將領域狀態寫入 ORM 欄位（純資料轉換，無 I/O）。
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Iterable
from uuid import UUID

from src.contexts.integration_operations.domain.entities import (
    AuditLog,
    ImportJob,
    NotificationJob,
    OcrJob,
    OcrResult,
)
from src.contexts.integration_operations.domain.value_objects import (
    ActionCode,
    ActorType,
    Confidence,
    ImportJobType,
    ImportSourceName,
    ImportSourceRef,
    JobLifecycleStatus,
    NotificationChannel,
    NotificationJobStatus,
    NotificationPayload,
    OcrFieldName,
    OcrProviderCode,
    ResourceId,
    ResourceType,
    TemplateCode,
)
from src.contexts.integration_operations.infra.schema import (
    AuditLogs,
    ImportJobs,
    NotificationJobs,
    OcrJobs,
    OcrResults,
)


def ocr_job_to_rows(job: OcrJob) -> tuple[OcrJobs, list[OcrResults]]:
    """將 OcrJob 聚合轉成主表列與結果列（不含 session）。"""
    main = OcrJobs(
        ocr_job_id=job.ocr_job_id,
        attachment_id=job.attachment_id,
        provider_code=job.provider_code.value,
        status=job.status.value,
        started_at=job.started_at,
        finished_at=job.finished_at,
        error_message=job.error_message,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )
    children: list[OcrResults] = []
    for r in job.results:
        children.append(
            OcrResults(
                ocr_result_id=r.ocr_result_id,
                attachment_id=r.attachment_id,
                field_name=r.field_name.value,
                field_value=r.field_value,
                confidence=r.confidence.value if r.confidence is not None else None,
                raw_json=r.raw_json,
                created_at=r.created_at,
            )
        )
    return main, children


def ocr_job_from_rows(job_row: OcrJobs, result_rows: Iterable[OcrResults]) -> OcrJob:
    """由主表列與結果列還原 OcrJob 聚合。"""
    results: list[OcrResult] = []
    for rr in sorted(result_rows, key=lambda x: x.created_at):
        conf: Confidence | None
        if rr.confidence is None:
            conf = None
        else:
            c = rr.confidence
            conf = Confidence(c if isinstance(c, Decimal) else Decimal(str(c)))
        results.append(
            OcrResult.new(
                attachment_id=rr.attachment_id,
                field_name=OcrFieldName(rr.field_name),
                field_value=rr.field_value,
                confidence=conf,
                raw_json=dict(rr.raw_json) if rr.raw_json is not None else None,
                created_at=rr.created_at,
                ocr_result_id=rr.ocr_result_id,
            )
        )
    return OcrJob(
        ocr_job_id=job_row.ocr_job_id,
        attachment_id=job_row.attachment_id,
        provider_code=OcrProviderCode(job_row.provider_code),
        status=JobLifecycleStatus(job_row.status),
        started_at=job_row.started_at,
        finished_at=job_row.finished_at,
        error_message=job_row.error_message,
        created_at=job_row.created_at,
        updated_at=job_row.updated_at,
        _results=results,
    )


def notification_job_to_row(job: NotificationJob) -> NotificationJobs:
    return NotificationJobs(
        notification_job_id=job.notification_job_id,
        channel=job.channel.value,
        recipient=job.recipient,
        template_code=job.template_code.value,
        payload_json=dict(job.payload.data),
        status=job.status.value,
        sent_at=job.sent_at,
        error_message=job.error_message,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


def notification_job_from_row(row: NotificationJobs) -> NotificationJob:
    return NotificationJob(
        notification_job_id=row.notification_job_id,
        channel=NotificationChannel(row.channel),
        recipient=row.recipient,
        template_code=TemplateCode(row.template_code),
        payload=NotificationPayload(row.payload_json),
        status=NotificationJobStatus(row.status),
        sent_at=row.sent_at,
        error_message=row.error_message,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def import_job_to_row(job: ImportJob) -> ImportJobs:
    return ImportJobs(
        import_job_id=job.import_job_id,
        job_type=job.job_type.value,
        source_name=job.source_name.value,
        source_ref=job.source_ref.value,
        status=job.status.value,
        started_at=job.started_at,
        finished_at=job.finished_at,
        result_summary=job.result_summary,
        error_message=job.error_message,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


def import_job_from_row(row: ImportJobs) -> ImportJob:
    return ImportJob(
        import_job_id=row.import_job_id,
        job_type=ImportJobType(row.job_type),
        source_name=ImportSourceName(row.source_name),
        source_ref=ImportSourceRef(value=row.source_ref),
        status=JobLifecycleStatus(row.status),
        started_at=row.started_at,
        finished_at=row.finished_at,
        result_summary=row.result_summary,
        error_message=row.error_message,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def audit_log_to_row(log: AuditLog) -> AuditLogs:
    return AuditLogs(
        audit_log_id=log.audit_log_id,
        actor_user_id=log.actor_user_id,
        actor_type=log.actor_type.value,
        action_code=log.action_code.value,
        resource_type=log.resource_type.value,
        resource_id=log.resource_id.value,
        before_json=_snapshot_to_json(log.before_snapshot.raw),
        after_json=_snapshot_to_json(log.after_snapshot.raw),
        client_ip=log.client_ip,
        created_at=log.created_at,
    )


def _snapshot_to_json(raw: dict[str, Any] | list[Any] | None) -> Any:
    if raw is None:
        return None
    if isinstance(raw, dict):
        return dict(raw)
    return list(raw)


def audit_log_from_row(row: AuditLogs) -> AuditLog:
    return AuditLog.record(
        actor_user_id=row.actor_user_id,
        actor_type=ActorType(row.actor_type),
        action_code=ActionCode(row.action_code),
        resource_type=ResourceType(row.resource_type),
        resource_id=ResourceId(row.resource_id),
        before=row.before_json,
        after=row.after_json,
        created_at=row.created_at,
        client_ip=str(row.client_ip) if row.client_ip is not None else None,
        audit_log_id=row.audit_log_id,
    )
