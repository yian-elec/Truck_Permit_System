"""
Permit 建立前資料載入之抽象（結構化子型別）。

責任：讓 **PermitServiceContext** 可注入 **PermitIssuanceContextReader** 或測試用 stub，
而不綁死具體類別名稱。
"""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from src.contexts.permit_document.app.services.integrations.permit_issuance_context_reader import (
    PermitIssuanceSnapshot,
)


class PermitIssuanceLoadPort(Protocol):
    """與 **PermitIssuanceContextReader.load** 對齊之最小介面。"""

    def load(self, application_id: UUID) -> PermitIssuanceSnapshot:
        ...
