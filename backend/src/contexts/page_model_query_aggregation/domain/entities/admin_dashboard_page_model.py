"""
管理者 Dashboard Page Model（Aggregate Root）。

責任：對應 `GET …/dashboard-model`；定義儀表板應呈現之**匯總指標**與**作業活動**兩大區塊，
供 App 層從多來源彙整數字與列表，領域僅約束區塊存在與順序。
"""

from __future__ import annotations

from dataclasses import dataclass

from ..services.page_model_section_catalog import (
    ADMIN_METRICS,
    ADMIN_OPS_FEED,
    PageModelSectionCatalog,
)
from ..value_objects import ModelContractVersion, PageModelKind, UpstreamFeedRole
from ._invariants import assert_closed_section_graph
from .page_model_section_spec import PageModelSectionSpec


@dataclass(frozen=True)
class AdminDashboardPageModel:
    """
    管理者儀表板 Page Model 聚合根。

    責任：`compose` 產出固定雙區塊——指標匯總優先、Ops 活動次級（依賴前者作為儀表板上下文之前置語意）。
    """

    kind: PageModelKind
    contract_version: ModelContractVersion
    sections: tuple[PageModelSectionSpec, ...]

    @classmethod
    def compose(cls, catalog: PageModelSectionCatalog) -> AdminDashboardPageModel:
        """
        組出管理者儀表板 Page Model。

        責任：兩區塊皆標為必填占位；若某來源暫無資料，App 層應回傳結構化空集合而非移除區塊
        （與申請人首頁 Ops 快照之「非必填」策略區隔，儀表板維持版面穩定）。
        """
        sections: tuple[PageModelSectionSpec, ...] = (
            PageModelSectionSpec(
                section_code=ADMIN_METRICS,
                sort_order=0,
                is_required_for_render=True,
                feed_roles=frozenset({UpstreamFeedRole.ADMIN_METRICS_AGGREGATE}),
            ),
            PageModelSectionSpec(
                section_code=ADMIN_OPS_FEED,
                sort_order=1,
                is_required_for_render=True,
                feed_roles=frozenset({UpstreamFeedRole.OPS_ACTIVITY_FEED}),
                prerequisite_section_codes=frozenset({ADMIN_METRICS}),
            ),
        )
        assert_closed_section_graph(sections)
        catalog.assert_all_registered(tuple(s.section_code for s in sections))
        return cls(
            kind=PageModelKind.ADMIN_DASHBOARD,
            contract_version=ModelContractVersion(major=1),
            sections=sections,
        )
