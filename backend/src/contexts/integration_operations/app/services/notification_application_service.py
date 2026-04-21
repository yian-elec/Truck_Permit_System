"""
UC-OPS-02 — 通知用例服務。

責任：建立 notification job、呼叫 DispatchPort、依結果更新 Domain 狀態並持久化。
"""

from __future__ import annotations

from datetime import datetime, timezone

from shared.core.logger.logger import logger

from src.contexts.integration_operations.app.dtos import (
    CreateNotificationJobInputDTO,
    CreateNotificationJobOutputDTO,
    DispatchNotificationInputDTO,
    DispatchNotificationOutputDTO,
)
from src.contexts.integration_operations.app.errors import OpsConflictError, OpsExternalDependencyError, OpsResourceNotFoundError
from src.contexts.integration_operations.domain.entities import NotificationJob
from src.contexts.integration_operations.domain.errors import InvalidDomainValueError, InvalidJobStateError
from src.contexts.integration_operations.domain.repositories import NotificationJobRepository
from src.contexts.integration_operations.domain.value_objects import NotificationChannel, NotificationPayload, TemplateCode

from .ports import NotificationDispatchPort


class NotificationApplicationService:
    """協調通知聚合、Repository 與發送埠。"""

    def __init__(
        self,
        notification_job_repository: NotificationJobRepository,
        dispatch_port: NotificationDispatchPort,
    ) -> None:
        self._repo = notification_job_repository
        self._dispatch = dispatch_port

    def create_job(self, dto: CreateNotificationJobInputDTO) -> CreateNotificationJobOutputDTO:
        """依業務事件建立待送達之 notification job。"""
        now = datetime.now(timezone.utc)
        logger.info(
            "NotificationApplicationService.create_job "
            f"channel={dto.channel} template={dto.template_code}"
        )
        try:
            job = NotificationJob.create(
                channel=NotificationChannel(dto.channel),
                recipient=dto.recipient,
                template_code=TemplateCode(dto.template_code),
                payload=NotificationPayload(dto.payload),
                now=now,
            )
        except InvalidDomainValueError as e:
            logger.warn(f"notification job validation failed: {e}")
            raise

        self._repo.save(job)
        return CreateNotificationJobOutputDTO(
            notification_job_id=job.notification_job_id,
            status=job.status.value,
        )

    def dispatch_pending_job(self, dto: DispatchNotificationInputDTO) -> DispatchNotificationOutputDTO:
        """對 pending job 套用模板並呼叫 provider；成功 sent，失敗保留錯誤。"""
        now = datetime.now(timezone.utc)
        job = self._repo.find_by_id(dto.notification_job_id)
        if job is None:
            raise OpsResourceNotFoundError(f"notification job not found: {dto.notification_job_id}")

        try:
            self._dispatch.dispatch(
                channel=job.channel.value,
                recipient=job.recipient,
                template_code=job.template_code.value,
                payload=dict(job.payload.data),
            )
        except Exception as e:
            logger.error(f"notification dispatch failed: {e}")
            try:
                msg = (str(e).strip() or "notification dispatch failed")[:20000]
                job.mark_failed(msg, now)
            except (InvalidJobStateError, InvalidDomainValueError) as inner:
                raise OpsConflictError(str(inner)) from inner
            self._repo.save(job)
            raise OpsExternalDependencyError(
                f"notification provider failed: {e}",
                details={"notification_job_id": str(dto.notification_job_id)},
            ) from e

        try:
            job.mark_sent(now)
        except (InvalidJobStateError, InvalidDomainValueError) as e:
            raise OpsConflictError(str(e)) from e

        self._repo.save(job)
        return DispatchNotificationOutputDTO(
            notification_job_id=job.notification_job_id,
            status=job.status.value,
            sent_at=job.sent_at,
            error_message=job.error_message,
        )
