"""
Review App 層對外埠（通知、可擴充之整合點）。

責任：與 Application context 之 `ApplicationEventPublisher` 分離，專責審查側通知／待辦推送；
預設提供空實作供測試與本地開發。
"""

from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID


class ReviewNotificationPort(Protocol):
    """
    審查流程對外通知（補件、駁回等）。

    責任：實作可對接 email、站內信、Webhook；payload 為純資料字典。
    """

    def notify(self, *, channel: str, payload: dict[str, Any]) -> None:
        """channel 建議值：supplement_required | application_rejected | task_assigned。"""
        ...


class NoopReviewNotificationPort:
    """不發送任何通知。"""

    def notify(self, *, channel: str, payload: dict[str, Any]) -> None:
        _ = (channel, payload)


def supplement_notification_payload(
    *,
    application_id: UUID,
    supplement_request_id: UUID,
    message: str,
) -> dict[str, Any]:
    """組補件通知之建議 payload 結構。"""
    return {
        "application_id": str(application_id),
        "supplement_request_id": str(supplement_request_id),
        "message": message,
    }
