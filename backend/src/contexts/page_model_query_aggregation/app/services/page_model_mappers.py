"""
Domain 聚合／區塊規格 → 應用層 DTO 映射。

責任：僅做結構轉換，不包含業務規則；規則留在 Domain `compose` 與 Value Object。
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from src.contexts.page_model_query_aggregation.app.dtos.page_model_dtos import (
    PageModelQueryResultDTO,
    PageSectionItemDTO,
)
from src.contexts.page_model_query_aggregation.domain.entities.page_model_section_spec import (
    PageModelSectionSpec,
)


def page_model_section_spec_to_dto(spec: PageModelSectionSpec) -> PageSectionItemDTO:
    """將單一 `PageModelSectionSpec` 轉為 API 用區塊 DTO。"""
    roles = sorted(spec.feed_roles, key=lambda r: r.value)
    pres = sorted(spec.prerequisite_section_codes, key=lambda c: c.value)
    return PageSectionItemDTO(
        section_code=spec.section_code.value,
        sort_order=spec.sort_order,
        is_required_for_render=spec.is_required_for_render,
        feed_roles=tuple(r.value for r in roles),
        prerequisite_section_codes=tuple(c.value for c in pres),
    )


def aggregate_to_page_model_result_dto(
    aggregate: Any,
    *,
    payload_by_section: dict[str, Any] | None = None,
) -> PageModelQueryResultDTO:
    """
    將任一 Page Model 聚合根轉為 `PageModelQueryResultDTO`。

    責任：讀取聚合上之 `kind`／`contract_version`／`sections`／可選 `application_id`（surrogate）；
    `payload_by_section` 由呼叫端填入（通常為下游 context 查詢結果，本函式預設空 dict）。
    """
    app_id: UUID | None = None
    surrogate = getattr(aggregate, "application_id", None)
    if surrogate is not None:
        app_id = surrogate.value

    sections = tuple(page_model_section_spec_to_dto(s) for s in aggregate.sections)
    return PageModelQueryResultDTO(
        page_kind=aggregate.kind.value,
        contract_version_major=aggregate.contract_version.major,
        application_id=app_id,
        sections=sections,
        payload_by_section=dict(payload_by_section or {}),
    )
