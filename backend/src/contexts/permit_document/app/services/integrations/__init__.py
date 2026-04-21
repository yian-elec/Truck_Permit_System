"""
跨 Bounded Context 之讀取與組裝（Application / Routing → Permit 用例）。

責任：與 **ports**（抽象出站埠）分離；此目錄放「主動讀取他 context」之整合程式，
不屬單一用例服務本體，避免 `services` 根目錄檔案過多、角色混淆。
"""

from .permit_issuance_context_reader import (
    PermitIssuanceContextReader,
    PermitIssuanceSnapshot,
    build_permit_no_from_application,
    build_route_summary_text_for_plan,
)

__all__ = [
    "PermitIssuanceSnapshot",
    "PermitIssuanceContextReader",
    "build_route_summary_text_for_plan",
    "build_permit_no_from_application",
]
