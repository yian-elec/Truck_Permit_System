"""
Page Model 查詢用例服務 — 對應規格 11 之四條聚合 read model API。

責任：
- 呼叫 Domain 聚合 `compose`，將結果映射為 `PageModelQueryResultDTO`；
- 解析輸入 DTO（如生命週期字串）為領域 Value Object；
- 可選協調 Infra：`snapshots_repository` 讀快取／寫快取（單次 `get_session` 交易由 Repository 封閉）；
- 以 `raise_page_model_domain_as_app` 統一將領域錯誤轉為 App 錯誤。

不包含：下游 Application／Review 等 context 之實際資料填充（`payload_by_section` 預留擴充）。
"""

from __future__ import annotations

from uuid import UUID, uuid4

from src.contexts.page_model_query_aggregation.app.dtos.page_model_dtos import (
    AdminDashboardPageInputDTO,
    ApplicantApplicationEditorInputDTO,
    ApplicantApplicationHomeInputDTO,
    PageModelQueryResultDTO,
    ReviewApplicationPageInputDTO,
)
from src.contexts.page_model_query_aggregation.app.errors import (
    PageModelValidationAppError,
    raise_page_model_domain_as_app,
)
from src.contexts.page_model_query_aggregation.app.services.page_model_mappers import (
    aggregate_to_page_model_result_dto,
)
from src.contexts.page_model_query_aggregation.app.services.page_model_service_context import (
    PageModelServiceContext,
)
from src.contexts.page_model_query_aggregation.domain import (
    AdminDashboardPageModel,
    ApplicantApplicationEditorPageModel,
    ApplicantApplicationHomePageModel,
    ApplicationLifecyclePhase,
    ApplicationLifecycleSnapshot,
    ApplicationSurrogateId,
    ReviewApplicationPageModel,
)


class PageModelQueryApplicationService:
    """
    Page Model 查詢用例之應用服務。

    責任：對外邊界為本類別之公開方法；不直接處理 HTTP，由 API Controller 呼叫並轉換回應包裝。
    """

    def __init__(self, ctx: PageModelServiceContext | None = None) -> None:
        self._ctx = ctx or PageModelServiceContext()

    # ------------------------------------------------------------------
    # 公開用例（對應四條 GET Page Model）
    # ------------------------------------------------------------------

    def get_applicant_application_home_model(
        self,
        inp: ApplicantApplicationHomeInputDTO,
        *,
        prefer_cache: bool = False,
        persist_snapshot: bool = False,
    ) -> PageModelQueryResultDTO:
        """
        UC：申請人首頁 Page Model（`GET …/application-home-model`）。

        參數 `prefer_cache`：為 True 且已注入 `snapshots_repository` 時，先嘗試依快取鍵讀取；
        反序列化失敗則退回 Domain 組版。
        參數 `persist_snapshot`：為 True 且已注入 repository 時，於組版成功後最佳努力寫入一筆快照（鍵已存在則略過）。
        """
        cache_key = _cache_key_applicant_home(inp.actor_user_id)
        if prefer_cache and self._ctx.snapshots_repository is not None:
            cached = _try_load_cached_dto(self._ctx.snapshots_repository, cache_key)
            if cached is not None:
                return cached

        def _compose() -> PageModelQueryResultDTO:
            agg = ApplicantApplicationHomePageModel.compose(self._ctx.section_catalog)
            return aggregate_to_page_model_result_dto(agg)

        dto = raise_page_model_domain_as_app(_compose)
        self._best_effort_persist_snapshot(
            cache_key=cache_key,
            dto=dto,
            persist=persist_snapshot,
            application_id=None,
        )
        return dto

    def get_applicant_application_editor_model(
        self,
        inp: ApplicantApplicationEditorInputDTO,
        *,
        prefer_cache: bool = False,
        persist_snapshot: bool = False,
    ) -> PageModelQueryResultDTO:
        """UC：申請人案件編輯器 Page Model（`GET …/applications/{id}/editor-model`）。"""
        lifecycle = _lifecycle_snapshot_from_editor_input(inp)
        surrogate = ApplicationSurrogateId(inp.application_id)
        cache_key = _cache_key_applicant_editor(inp.application_id, lifecycle)

        if prefer_cache and self._ctx.snapshots_repository is not None:
            cached = _try_load_cached_dto(self._ctx.snapshots_repository, cache_key)
            if cached is not None:
                return cached

        def _compose() -> PageModelQueryResultDTO:
            agg = ApplicantApplicationEditorPageModel.compose(
                self._ctx.section_catalog,
                application_id=surrogate,
                lifecycle=lifecycle,
            )
            return aggregate_to_page_model_result_dto(agg)

        dto = raise_page_model_domain_as_app(_compose)
        self._best_effort_persist_snapshot(
            cache_key=cache_key,
            dto=dto,
            persist=persist_snapshot,
            application_id=inp.application_id,
        )
        return dto

    def get_review_application_page_model(
        self,
        inp: ReviewApplicationPageInputDTO,
        *,
        prefer_cache: bool = False,
        persist_snapshot: bool = False,
    ) -> PageModelQueryResultDTO:
        """UC：審查員案件 Page Model（`GET …/review-model`）。"""
        surrogate = ApplicationSurrogateId(inp.application_id)
        cache_key = _cache_key_review_application(inp.application_id, inp.include_permit_section)

        if prefer_cache and self._ctx.snapshots_repository is not None:
            cached = _try_load_cached_dto(self._ctx.snapshots_repository, cache_key)
            if cached is not None:
                return cached

        def _compose() -> PageModelQueryResultDTO:
            agg = ReviewApplicationPageModel.compose(
                self._ctx.section_catalog,
                application_id=surrogate,
                include_permit_section=inp.include_permit_section,
            )
            return aggregate_to_page_model_result_dto(agg)

        dto = raise_page_model_domain_as_app(_compose)
        self._best_effort_persist_snapshot(
            cache_key=cache_key,
            dto=dto,
            persist=persist_snapshot,
            application_id=inp.application_id,
        )
        return dto

    def get_admin_dashboard_page_model(
        self,
        inp: AdminDashboardPageInputDTO,
        *,
        prefer_cache: bool = False,
        persist_snapshot: bool = False,
    ) -> PageModelQueryResultDTO:
        """UC：管理者儀表板 Page Model（`GET …/dashboard-model`）。"""
        cache_key = _cache_key_admin_dashboard(inp.actor_user_id)

        if prefer_cache and self._ctx.snapshots_repository is not None:
            cached = _try_load_cached_dto(self._ctx.snapshots_repository, cache_key)
            if cached is not None:
                return cached

        def _compose() -> PageModelQueryResultDTO:
            agg = AdminDashboardPageModel.compose(self._ctx.section_catalog)
            return aggregate_to_page_model_result_dto(agg)

        dto = raise_page_model_domain_as_app(_compose)
        self._best_effort_persist_snapshot(
            cache_key=cache_key,
            dto=dto,
            persist=persist_snapshot,
            application_id=None,
        )
        return dto

    # ------------------------------------------------------------------
    # 可選 Infra：快取（讀／寫各由獨立 Repository 呼叫完成交易）
    # ------------------------------------------------------------------

    def _best_effort_persist_snapshot(
        self,
        *,
        cache_key: str,
        dto: PageModelQueryResultDTO,
        persist: bool,
        application_id: UUID | None,
    ) -> None:
        """
        若 `persist` 且已設定 repository，則在快取鍵尚無列時寫入一筆快照。

        責任：不拋出至用例呼叫端（最佳努力）；重複鍵或 DB 錯誤時靜默略過，避免影響主 read path。
        """
        if not persist or self._ctx.snapshots_repository is None:
            return
        try:
            existing = self._ctx.snapshots_repository.get_by_cache_key(cache_key)
            if existing is not None:
                return
            from src.contexts.page_model_query_aggregation.infra.schema.page_model_snapshots import (
                PageModelSnapshots,
            )

            row = PageModelSnapshots(
                snapshot_id=uuid4(),
                page_kind=dto.page_kind,
                application_id=application_id,
                cache_key=cache_key,
                payload_json=dto.to_cache_payload_dict(),
                contract_version_major=dto.contract_version_major,
                notes=None,
            )
            self._ctx.snapshots_repository.add(row)
        except Exception:
            return


def _lifecycle_snapshot_from_editor_input(
    inp: ApplicantApplicationEditorInputDTO,
) -> ApplicationLifecycleSnapshot:
    """將編輯器輸入 DTO 轉為領域生命週期快照；非法 phase 字串拋 `PageModelValidationAppError`。"""
    try:
        phase = ApplicationLifecyclePhase(inp.lifecycle_phase)
    except ValueError as e:
        allowed = ", ".join(sorted(p.value for p in ApplicationLifecyclePhase))
        raise PageModelValidationAppError(
            f"無效的生命週期階段: {inp.lifecycle_phase!r}；允許值: {allowed}",
            {
                "field": "lifecycle_phase",
                "allowed": [p.value for p in ApplicationLifecyclePhase],
            },
        ) from e
    return ApplicationLifecycleSnapshot(
        phase=phase,
        has_active_route_plan=inp.has_active_route_plan,
        has_pending_supplement_request=inp.has_pending_supplement_request,
        has_issued_permit_documents=inp.has_issued_permit_documents,
    )


def _cache_key_applicant_home(actor_user_id: UUID) -> str:
    return f"page:applicant:home:{actor_user_id}"


def _cache_key_applicant_editor(application_id: UUID, life: ApplicationLifecycleSnapshot) -> str:
    return (
        f"page:applicant:editor:{application_id}:"
        f"{life.phase.value}:rp{int(life.has_active_route_plan)}:"
        f"sp{int(life.has_pending_supplement_request)}:pd{int(life.has_issued_permit_documents)}"
    )


def _cache_key_review_application(application_id: UUID, include_permit: bool) -> str:
    return f"page:review:application:{application_id}:perm{int(include_permit)}"


def _cache_key_admin_dashboard(actor_user_id: UUID) -> str:
    return f"page:admin:dashboard:{actor_user_id}"


def _try_load_cached_dto(repo: object, cache_key: str) -> PageModelQueryResultDTO | None:
    """自快照表還原 DTO；失敗回傳 None。"""
    get_by = getattr(repo, "get_by_cache_key", None)
    if get_by is None:
        return None
    try:
        row = get_by(cache_key)
        if row is None or not getattr(row, "payload_json", None):
            return None
        return PageModelQueryResultDTO.from_cache_payload_dict(dict(row.payload_json))
    except (KeyError, TypeError, ValueError, AttributeError):
        return None
