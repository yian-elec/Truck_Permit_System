"""
審查員 Application Review Page Model（Aggregate Root）。

責任：對應 `GET …/review-model`；組出審查工作臺所需之唯讀案件／路徑區塊與可互動審查區塊，
並以領域規則約束區塊依賴（審查區必須在案件摘要之後）。
"""

from __future__ import annotations

from dataclasses import dataclass

from ..services.page_model_section_catalog import (
    PageModelSectionCatalog,
    REVIEW_CASE_READONLY,
    REVIEW_PERMIT_READONLY,
    REVIEW_ROUTING_READONLY,
    REVIEW_WORKSPACE,
)
from ..value_objects import (
    ApplicationSurrogateId,
    ModelContractVersion,
    PageModelKind,
    UpstreamFeedRole,
)
from ._invariants import assert_closed_section_graph
from .page_model_section_spec import PageModelSectionSpec


@dataclass(frozen=True)
class ReviewApplicationPageModel:
    """
    審查員單一案件 Page Model 聚合根。

    責任：攜帶 `application_id` 與審查導向之區塊規格；不執行審查決策，只定義畫面資料邊界與載入角色。
    """

    kind: PageModelKind
    contract_version: ModelContractVersion
    application_id: ApplicationSurrogateId
    sections: tuple[PageModelSectionSpec, ...]

    @classmethod
    def compose(
        cls,
        catalog: PageModelSectionCatalog,
        *,
        application_id: ApplicationSurrogateId,
        include_permit_section: bool = True,
    ) -> ReviewApplicationPageModel:
        """
        組出審查頁 Page Model。

        參數 `include_permit_section`：
        - **True**（預設）：保留許可／文件唯讀區，App 層可於核准後填入；未核准時可回空。
        - **False**：在產品策略不於審查頁顯示文件時關閉該區塊（仍不查 Infra，僅縮減契約）。

        責任：固定順序為案件摘要 → 路徑唯讀 → 審查工作區 →（可選）許可唯讀。
        """
        case_only = frozenset({REVIEW_CASE_READONLY})
        sections_list: list[PageModelSectionSpec] = [
            PageModelSectionSpec(
                section_code=REVIEW_CASE_READONLY,
                sort_order=0,
                is_required_for_render=True,
                feed_roles=frozenset({UpstreamFeedRole.APPLICATION_CASE_CORE}),
            ),
            PageModelSectionSpec(
                section_code=REVIEW_ROUTING_READONLY,
                sort_order=1,
                is_required_for_render=True,
                feed_roles=frozenset({UpstreamFeedRole.ROUTING_REQUEST_AND_PLANS}),
                prerequisite_section_codes=case_only,
            ),
            PageModelSectionSpec(
                section_code=REVIEW_WORKSPACE,
                sort_order=2,
                is_required_for_render=True,
                feed_roles=frozenset({UpstreamFeedRole.REVIEW_TASKS_AND_DECISIONS}),
                prerequisite_section_codes=case_only,
            ),
        ]
        if include_permit_section:
            sections_list.append(
                PageModelSectionSpec(
                    section_code=REVIEW_PERMIT_READONLY,
                    sort_order=3,
                    is_required_for_render=False,
                    feed_roles=frozenset({UpstreamFeedRole.PERMIT_DOCUMENTS}),
                    prerequisite_section_codes=case_only,
                )
            )

        sections = tuple(sections_list)
        assert_closed_section_graph(sections)
        catalog.assert_all_registered(tuple(s.section_code for s in sections))
        return cls(
            kind=PageModelKind.REVIEW_APPLICATION,
            contract_version=ModelContractVersion(major=1),
            application_id=application_id,
            sections=sections,
        )
