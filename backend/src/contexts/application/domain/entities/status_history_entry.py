"""
案件狀態變更歷史紀錄（實體／不可變紀錄）。

責任：對應 application.status_histories；「補件需保留歷史」透過僅附加新列、不修改舊列達成。
領域層每次狀態轉移應新增一筆，由 Aggregate 呼叫。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class StatusHistoryEntry:
    """
    單次狀態轉移之不可變快照。

    責任：保存 from_status／to_status、操作者、原因與時間，供 timeline 與稽核還原。
    """

    history_id: UUID
    application_id: UUID
    from_status: str | None
    to_status: str
    changed_by: UUID | None
    reason: str | None
    created_at: datetime
