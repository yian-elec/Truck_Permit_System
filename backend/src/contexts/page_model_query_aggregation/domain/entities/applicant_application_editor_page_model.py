"""
申請人 Application Editor Page Model（Aggregate Root）。

責任：對應 `GET …/applications/{applicationId}/editor-model`；依**注入之生命週期快照**決定
是否露出路徑、補件、許可文件等區塊，體現「同一路徑、不同階段不同區塊組合」的領域規則。
"""

from __future__ import annotations

from dataclasses import dataclass

from ..services.page_model_section_catalog import (
    EDITOR_ATTACHMENTS,
    EDITOR_CASE_CORE,
    EDITOR_PERMIT_DOCUMENTS,
    EDITOR_ROUTING,
    EDITOR_SUPPLEMENT_WORKSPACE,
    EDITOR_VEHICLES,
    PageModelSectionCatalog,
)
from ..value_objects import (
    ApplicationLifecycleSnapshot,
    ApplicationSurrogateId,
    ModelContractVersion,
    PageModelKind,
    UpstreamFeedRole,
)
from ._invariants import assert_closed_section_graph
from .page_model_section_spec import PageModelSectionSpec


@dataclass(frozen=True)
class ApplicantApplicationEditorPageModel:
    """
    申請人單一案件編輯器 Page Model 聚合根。

    責任：
    - 綁定 `application_id`（surrogate）與建立當下之 `lifecycle` 快照
    - `compose` 依快照規則動態組裝區塊集合並驗證不變條件
    """

    kind: PageModelKind
    contract_version: ModelContractVersion
    application_id: ApplicationSurrogateId
    lifecycle: ApplicationLifecycleSnapshot
    sections: tuple[PageModelSectionSpec, ...]

    @classmethod
    def compose(
        cls,
        catalog: PageModelSectionCatalog,
        *,
        application_id: ApplicationSurrogateId,
        lifecycle: ApplicationLifecycleSnapshot,
    ) -> ApplicantApplicationEditorPageModel:
        """
        依案件身分與生命週期組出編輯器 Page Model。

        責任：
        - 核心案件、車輛、附件區塊為**固定基底**（必填）
        - 路徑區塊僅在申請人可編輯路徑之階段露出
        - 補件工作區在有補件需求或處於補件階段時露出
        - 許可／文件區僅在已知有關聯文件時露出（避免空區塊）
        """
        core_prereq = frozenset({EDITOR_CASE_CORE})
        base: list[PageModelSectionSpec] = [
            PageModelSectionSpec(
                section_code=EDITOR_CASE_CORE,
                sort_order=0,
                is_required_for_render=True,
                feed_roles=frozenset({UpstreamFeedRole.APPLICATION_CASE_CORE}),
            ),
            PageModelSectionSpec(
                section_code=EDITOR_VEHICLES,
                sort_order=1,
                is_required_for_render=True,
                feed_roles=frozenset({UpstreamFeedRole.APPLICATION_VEHICLES}),
                prerequisite_section_codes=core_prereq,
            ),
            PageModelSectionSpec(
                section_code=EDITOR_ATTACHMENTS,
                sort_order=2,
                is_required_for_render=True,
                feed_roles=frozenset({UpstreamFeedRole.APPLICATION_ATTACHMENTS}),
                prerequisite_section_codes=core_prereq,
            ),
        ]
        next_order = 3

        if lifecycle.applicant_may_edit_routing() or lifecycle.has_active_route_plan:
            base.append(
                PageModelSectionSpec(
                    section_code=EDITOR_ROUTING,
                    sort_order=next_order,
                    is_required_for_render=lifecycle.applicant_may_edit_routing(),
                    feed_roles=frozenset({UpstreamFeedRole.ROUTING_REQUEST_AND_PLANS}),
                    prerequisite_section_codes=core_prereq,
                )
            )
            next_order += 1

        if lifecycle.should_surface_supplement_workspace():
            base.append(
                PageModelSectionSpec(
                    section_code=EDITOR_SUPPLEMENT_WORKSPACE,
                    sort_order=next_order,
                    is_required_for_render=True,
                    feed_roles=frozenset({UpstreamFeedRole.REVIEW_TASKS_AND_DECISIONS}),
                    prerequisite_section_codes=core_prereq,
                )
            )
            next_order += 1

        if lifecycle.should_surface_permit_documents():
            base.append(
                PageModelSectionSpec(
                    section_code=EDITOR_PERMIT_DOCUMENTS,
                    sort_order=next_order,
                    is_required_for_render=False,
                    feed_roles=frozenset({UpstreamFeedRole.PERMIT_DOCUMENTS}),
                    prerequisite_section_codes=core_prereq,
                )
            )

        sections = tuple(base)
        assert_closed_section_graph(sections)
        catalog.assert_all_registered(tuple(s.section_code for s in sections))
        return cls(
            kind=PageModelKind.APPLICANT_APPLICATION_EDITOR,
            contract_version=ModelContractVersion(major=1),
            application_id=application_id,
            lifecycle=lifecycle,
            sections=sections,
        )
