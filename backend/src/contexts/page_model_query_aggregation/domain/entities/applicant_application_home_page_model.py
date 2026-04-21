"""
申請人 Application Home Page Model（Aggregate Root）。

責任：對應 `GET …/application-home-model` 之領域聚合邊界；決定首頁應包含哪些**邏輯區塊**
及其順序與上游餵入角色，並保證不變條件成立。實際文案與列表資料由 App 層依 `feed_roles` 填入。
"""

from __future__ import annotations

from dataclasses import dataclass

from ..services.page_model_section_catalog import (
    HOME_MY_APPLICATIONS,
    HOME_OPS_ACTIVITY_SNAPSHOT,
    HOME_SERVICE_OVERVIEW,
    HOME_USER_ACCOUNT,
    PageModelSectionCatalog,
)
from ..value_objects import (
    ModelContractVersion,
    PageModelKind,
    UpstreamFeedRole,
)
from ._invariants import assert_closed_section_graph
from .page_model_section_spec import PageModelSectionSpec


@dataclass(frozen=True)
class ApplicantApplicationHomePageModel:
    """
    申請人「案件首頁／入口」之 Page Model 聚合根。

    責任：
    - 透過 `compose` 建立凍結的區塊規格列表（不可在聚合外任意增刪）
    - 攜帶 `PageModelKind` 與契約版本供 API 回應標頭或本體標註
    - 不持有任何來自其他 context 的實體或 DTO
    """

    kind: PageModelKind
    contract_version: ModelContractVersion
    sections: tuple[PageModelSectionSpec, ...]

    @classmethod
    def compose(cls, catalog: PageModelSectionCatalog) -> ApplicantApplicationHomePageModel:
        """
        依產品預設規則組出申請人首頁 Page Model。

        責任：區塊為固定骨架——服務導覽、帳號摘要、我的案件、可選之 Ops 活動摘要；
        Ops 區塊標為非必填，App 層若無資料可回傳空占位。
        """
        sections: tuple[PageModelSectionSpec, ...] = (
            PageModelSectionSpec(
                section_code=HOME_SERVICE_OVERVIEW,
                sort_order=0,
                is_required_for_render=True,
                feed_roles=frozenset({UpstreamFeedRole.PUBLIC_SERVICE_COPY}),
            ),
            PageModelSectionSpec(
                section_code=HOME_USER_ACCOUNT,
                sort_order=1,
                is_required_for_render=True,
                feed_roles=frozenset({UpstreamFeedRole.USER_ACCOUNT_SUMMARY}),
            ),
            PageModelSectionSpec(
                section_code=HOME_MY_APPLICATIONS,
                sort_order=2,
                is_required_for_render=True,
                feed_roles=frozenset({UpstreamFeedRole.MY_APPLICATIONS_SUMMARY}),
                prerequisite_section_codes=frozenset({HOME_USER_ACCOUNT}),
            ),
            PageModelSectionSpec(
                section_code=HOME_OPS_ACTIVITY_SNAPSHOT,
                sort_order=3,
                is_required_for_render=False,
                feed_roles=frozenset({UpstreamFeedRole.OPS_ACTIVITY_FEED}),
                prerequisite_section_codes=frozenset({HOME_USER_ACCOUNT}),
            ),
        )
        assert_closed_section_graph(sections)
        catalog.assert_all_registered(tuple(s.section_code for s in sections))
        return cls(
            kind=PageModelKind.APPLICANT_APPLICATION_HOME,
            contract_version=ModelContractVersion(major=1),
            sections=sections,
        )
