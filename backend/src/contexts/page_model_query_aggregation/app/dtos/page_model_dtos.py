"""
Page_Model_Query_Aggregation — 用例輸入／輸出 DTO。

責任：
- 表達四條 Page Model API 對應之查詢輸入與回應結構；
- 與 Domain 聚合之 `compose` 結果分離，API 僅依賴本模組之 dataclass／欄位型別。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID


# ---------------------------------------------------------------------------
# 輸出：區塊與整體 Page Model（前端可直接對應之 read model 骨架）
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PageSectionItemDTO:
    """
    單一 Page Model 邏輯區塊（無實際業務 payload，僅契約／順序／資料來源角色）。

    責任：對應 Domain `PageModelSectionSpec` 之穩定輸出；`feed_roles` 供 App 後續或 BFF 決定要呼叫之下游 context。
    """

    section_code: str
    sort_order: int
    is_required_for_render: bool
    feed_roles: tuple[str, ...]
    prerequisite_section_codes: tuple[str, ...]


@dataclass(frozen=True)
class PageModelQueryResultDTO:
    """
    聚合型 Page Model 查詢結果（read model 骨架）。

    責任：攜帶 `page_kind`、`contract_version_major`、可選 `application_id` 與有序區塊列表；
    `payload_by_section` 預留由後續 orchestration 填入之下游資料（可為空 dict）。
    """

    page_kind: str
    contract_version_major: int
    application_id: UUID | None
    sections: tuple[PageSectionItemDTO, ...]
    payload_by_section: dict[str, Any]

    def to_cache_payload_dict(self) -> dict[str, Any]:
        """
        轉成可寫入 `page_model_snapshots.payload_json` 之純資料 dict（可 JSON 序列化）。

        責任：供 Infra 快取列使用，避免 ORM 直接依賴本 dataclass。
        """
        return {
            "page_kind": self.page_kind,
            "contract_version_major": self.contract_version_major,
            "application_id": str(self.application_id) if self.application_id else None,
            "sections": [
                {
                    "section_code": s.section_code,
                    "sort_order": s.sort_order,
                    "is_required_for_render": s.is_required_for_render,
                    "feed_roles": list(s.feed_roles),
                    "prerequisite_section_codes": list(s.prerequisite_section_codes),
                }
                for s in self.sections
            ],
            "payload_by_section": dict(self.payload_by_section),
        }

    @classmethod
    def from_cache_payload_dict(cls, data: dict[str, Any]) -> PageModelQueryResultDTO:
        """
        自快取 JSON 還原為 DTO（欄位不完整時拋錯由呼叫端處理）。

        責任：與 `to_cache_payload_dict` 對稱，供可選之讀快取路徑使用。
        """
        raw_sections = data.get("sections") or []
        sections: list[PageSectionItemDTO] = []
        for item in raw_sections:
            sections.append(
                PageSectionItemDTO(
                    section_code=str(item["section_code"]),
                    sort_order=int(item["sort_order"]),
                    is_required_for_render=bool(item["is_required_for_render"]),
                    feed_roles=tuple(str(x) for x in item.get("feed_roles", [])),
                    prerequisite_section_codes=tuple(
                        str(x) for x in item.get("prerequisite_section_codes", [])
                    ),
                )
            )
        app_raw = data.get("application_id")
        app_id: UUID | None
        if app_raw is None or app_raw == "":
            app_id = None
        else:
            app_id = UUID(str(app_raw))
        return cls(
            page_kind=str(data["page_kind"]),
            contract_version_major=int(data["contract_version_major"]),
            application_id=app_id,
            sections=tuple(sections),
            payload_by_section=dict(data.get("payload_by_section") or {}),
        )


# ---------------------------------------------------------------------------
# 輸入：四條用例
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ApplicantApplicationHomeInputDTO:
    """
    申請人首頁 Page Model 查詢輸入。

    責任：`actor_user_id` 供授權與快取鍵使用；組版規則本身不依賴使用者，但 API 層應驗證 JWT 與此欄位一致。
    """

    actor_user_id: UUID


@dataclass(frozen=True)
class ApplicantApplicationEditorInputDTO:
    """
    申請人案件編輯器 Page Model 查詢輸入。

    責任：攜帶案件識別與生命週期快照欄位；後者通常由 App 層先呼叫 Application／Review 等 context 組裝後填入。
    """

    actor_user_id: UUID
    application_id: UUID
    lifecycle_phase: str
    has_active_route_plan: bool = False
    has_pending_supplement_request: bool = False
    has_issued_permit_documents: bool = False


@dataclass(frozen=True)
class ReviewApplicationPageInputDTO:
    """
    審查員單一案件 Page Model 查詢輸入。

    責任：`include_permit_section` 對應 Domain `ReviewApplicationPageModel.compose` 之同名參數。
    """

    actor_user_id: UUID
    application_id: UUID
    include_permit_section: bool = True


@dataclass(frozen=True)
class AdminDashboardPageInputDTO:
    """
    管理者儀表板 Page Model 查詢輸入。

    責任：`actor_user_id` 供日後管理員角色／稽核使用；目前 Domain 組版不依賴該欄位。
    """

    actor_user_id: UUID
