"""
通知作業聚合（Aggregate Root）。

責任：對應 ops.notification_jobs 與 UC-OPS-02；封裝 channel、recipient、template、payload 與配送狀態。
成功時標記為 sent 並記錄 sent_at；失敗時保留 error_message，且終結後不可再變更。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from ..errors import InvalidDomainValueError, InvalidJobStateError
from ..value_objects import (
    NotificationChannel,
    NotificationJobStatus,
    NotificationPayload,
    TemplateCode,
)


@dataclass
class NotificationJob:
    """
    通知 Job 聚合根。

    責任：在領域內保證狀態僅能由 pending 轉為 sent 或 failed，與「套用模板、呼叫 provider」的
    App 編排分離；此處只關心狀態與欄位不變條件。
    """

    notification_job_id: UUID
    channel: NotificationChannel
    recipient: str
    template_code: TemplateCode
    payload: NotificationPayload
    status: NotificationJobStatus
    sent_at: datetime | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        r = (self.recipient or "").strip()
        if not r:
            raise InvalidDomainValueError("Notification recipient must be non-empty")
        if len(r) > 255:
            raise InvalidDomainValueError("Notification recipient exceeds max length 255")
        self.recipient = r

    @classmethod
    def create(
        cls,
        *,
        channel: NotificationChannel,
        recipient: str,
        template_code: TemplateCode,
        payload: NotificationPayload,
        now: datetime,
        notification_job_id: UUID | None = None,
    ) -> NotificationJob:
        """
        建立一筆待處理通知作業（對應 UC-OPS-02 建立 notification job）。

        由 submitted／supplement／approved／rejected 等事件觸發的編排在 App 層完成。
        """
        jid = notification_job_id or uuid4()
        st = NotificationJobStatus.pending()
        return cls(
            notification_job_id=jid,
            channel=channel,
            recipient=recipient,
            template_code=template_code,
            payload=payload,
            status=st,
            sent_at=None,
            error_message=None,
            created_at=now,
            updated_at=now,
        )

    def mark_sent(self, now: datetime) -> None:
        """標記已成功送達；僅允許自 pending 轉為 sent。"""
        if self.status.value != NotificationJobStatus.pending().value:
            raise InvalidJobStateError(
                "Only a pending notification job can be marked as sent",
                current_status=self.status.value,
            )
        self.status = NotificationJobStatus.sent()
        self.sent_at = now
        self.error_message = None
        self.updated_at = now

    def mark_failed(self, message: str, now: datetime) -> None:
        """標記送達失敗並保存錯誤；僅允許自 pending 轉為 failed。"""
        if self.status.value != NotificationJobStatus.pending().value:
            raise InvalidJobStateError(
                "Only a pending notification job can be marked as failed",
                current_status=self.status.value,
            )
        if not message or not message.strip():
            raise InvalidDomainValueError("Failure message is required for a failed notification job")
        self.status = NotificationJobStatus.failed()
        self.error_message = message.strip()
        self.sent_at = None
        self.updated_at = now
