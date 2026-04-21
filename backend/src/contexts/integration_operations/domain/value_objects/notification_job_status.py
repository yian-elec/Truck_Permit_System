"""
通知作業狀態（Value Object）。

責任：與 ops.notification_jobs.status 對應；通知為短流程，語意與 OCR／匯入的 lifecycle 分開。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..errors import InvalidDomainValueError


class NotificationDeliveryPhase(StrEnum):
    """
    通知 Job 的配送階段。

    責任：對應 UC-OPS-02（建立 job → 呼叫 provider → 成功 sent 或失敗保留錯誤）。
    """

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


@dataclass(frozen=True)
class NotificationJobStatus:
    """封裝 notification_jobs.status，僅允許已知階段。"""

    value: str

    def __post_init__(self) -> None:
        allowed = {p.value for p in NotificationDeliveryPhase}
        if self.value not in allowed:
            raise InvalidDomainValueError(
                f"Invalid notification job status: {self.value!r}; expected one of {sorted(allowed)}"
            )

    @classmethod
    def pending(cls) -> NotificationJobStatus:
        """已建立 job、尚未完成 provider 呼叫或結果尚未寫回。"""
        return cls(NotificationDeliveryPhase.PENDING.value)

    @classmethod
    def sent(cls) -> NotificationJobStatus:
        """已成功送達（對應 sent_at 可由 Aggregate 另行設定）。"""
        return cls(NotificationDeliveryPhase.SENT.value)

    @classmethod
    def failed(cls) -> NotificationJobStatus:
        """provider 失敗或不可重試之錯誤。"""
        return cls(NotificationDeliveryPhase.FAILED.value)

    def is_terminal(self) -> bool:
        """是否已終結（已送達或已失敗）。"""
        return self.value in (
            NotificationDeliveryPhase.SENT.value,
            NotificationDeliveryPhase.FAILED.value,
        )
