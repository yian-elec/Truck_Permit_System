"""
RestrictionEvaluationService — 候選路線與限制規則之領域服務。

責任：編排「先產出候選、再做規則檢核」之**業務順序語意**、命中排序（forbidden 優先於 warning）、
exception_road 對命中的覆蓋、分數加權與無路說明彙整。空間相交計算本身不在此類實作，
由 App 呼叫 Infra／Provider 產生原始 RuleHit 後，交由本服務套用領域規則。
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal
from typing import Iterable, List, Optional, Sequence, Tuple

from src.contexts.routing_restriction.domain.entities.restriction_rule import RestrictionRule
from src.contexts.routing_restriction.domain.entities.route_candidate import RouteCandidate
from src.contexts.routing_restriction.domain.errors import RoutingInvalidValueError
from src.contexts.routing_restriction.domain.value_objects.no_route_explanation import (
    NoRouteExplanation,
)
from src.contexts.routing_restriction.domain.value_objects.route_score import RouteScore
from src.contexts.routing_restriction.domain.value_objects.rule_hit import RuleHit
from src.contexts.routing_restriction.domain.value_objects.routing_enums import (
    HitSeverity,
    NoRouteReasonCode,
    RuleType,
)
from src.contexts.routing_restriction.domain.value_objects.vehicle_constraint import (
    VehicleConstraint,
)


class RoutingPipelinePolicy:
    """
    路線與限制檢核之管線策略（文件化不變式）。

    責任：集中描述核心規則，供 App／測試與文件引用；無狀態。
    """

    PIPELINE_ORDER = (
        "1) Obtain candidate routes from routing provider. "
        "2) Decompose into segments when required. "
        "3) Evaluate restriction rules against geometry/time/vehicle. "
        "4) Apply exception_road overrides. "
        "5) Score and determine feasibility; if none, emit structured no-route reason."
    )
    FORBIDDEN_DOMINATES_WARNING = (
        "HitSeverity.FORBIDDEN takes precedence over WARNING for feasibility and display ordering."
    )
    EXCEPTION_ROAD_OVERRIDES = (
        "FORBIDDEN hits tied to a segment marked is_exception_road may be suppressed "
        "for zone/road prohibition rule types."
    )
    VERSIONS_ON_PLAN = (
        "map_version and planning_version are owned by RoutePlan and must be preserved across replans."
    )


class RestrictionEvaluationService:
    """
    規則檢核與候選後處理之無狀態領域服務。

    責任：對已附帶 **rule_hits** 的 `RouteCandidate` 套用例外路段覆蓋、排序命中、
    計算分數與產生無路說明；**不**直接呼叫外部路網或 PostGIS。
    """

    WARNING_PENALTY = Decimal("1")
    FORBIDDEN_PENALTY = Decimal("10000")

    @classmethod
    def filter_rules_applicable_today(
        cls,
        rules: Sequence[RestrictionRule],
        *,
        vehicle: VehicleConstraint,
        on_date: date,
    ) -> List[RestrictionRule]:
        """
        依車重與曆日篩選可能適用之啟用規則。

        責任：時間窗之「當日幾點」是否命中須結合出發時間，由 `filter_rules_for_departure`
        或 App 層補齊；此處僅處理 active、effective_range 與重量閾值。
        """
        out: List[RestrictionRule] = []
        for r in rules:
            if not r.is_active:
                continue
            if not r.applies_on_calendar_date(on_date):
                continue
            if not r.applies_by_vehicle_weight(vehicle):
                continue
            out.append(r)
        return out

    @classmethod
    def filter_rules_for_departure(
        cls,
        rules: Sequence[RestrictionRule],
        *,
        departure: datetime,
        is_public_holiday: bool,
    ) -> List[RestrictionRule]:
        """
        在已通過曆日／車重篩選之規則上，再依 **出發時間** 與各規則之 `RestrictionWindow` 過濾。

        責任：補齊「申請時段 vs 禁行時段」之領域判斷；國定假日由呼叫端提供旗標（假日曆屬 App／Infra）。
        若規則無任何 time_windows，視為該日全日適用（仍受 `applies_on_calendar_date` 約束）。
        """
        return [
            r
            for r in rules
            if r.applies_at_departure(
                departure, is_public_holiday=is_public_holiday
            )
        ]

    @classmethod
    def sort_hits_forbidden_before_warning(cls, hits: Sequence[RuleHit]) -> List[RuleHit]:
        """
        命中列表排序：**FORBIDDEN 優先於 WARNING**（同級則維持穩定順序）。

        責任：滿足「forbidden 優先於一般 warning」之展示與處理順序；不改變集合內容。
        """
        severity_rank = {HitSeverity.FORBIDDEN: 0, HitSeverity.WARNING: 1}
        return sorted(hits, key=lambda h: severity_rank[h.severity])

    @classmethod
    def apply_exception_road_overrides(cls, candidate: RouteCandidate) -> RouteCandidate:
        """
        套用 **exception_road** 語意：若命中綁定之路段標記為例外可通行，則抑制該筆 **禁止類**
        FORBIDDEN 命中（禁區／禁路）。

        責任：不抑制 WARNING（避免掩蓋風險提示）；無 segment_index 之命中無法對路段覆蓋，保留原樣。
        """
        kept: List[RuleHit] = []
        suppress_types = frozenset({RuleType.FORBIDDEN_ZONE, RuleType.FORBIDDEN_ROAD})
        for h in candidate.rule_hits:
            if (
                h.segment_index is not None
                and candidate.segment_is_exception(h.segment_index)
                and h.rule_type in suppress_types
                and h.severity == HitSeverity.FORBIDDEN
            ):
                continue
            kept.append(h)
        return candidate.replace_rule_hits(kept)

    @classmethod
    def score_candidate(
        cls,
        candidate: RouteCandidate,
        *,
        base_score: Decimal,
    ) -> RouteCandidate:
        """
        依命中加權計算分數（越高越好之前提下，對 WARNING／未抑制之 FORBIDDEN 扣分）。

        責任：若仍存在 FORBIDDEN 命中，施以重罰使該候選在排序中落於可行候選之後；
        實際「是否可選」仍應以 `has_unsuppressed_forbidden_hit` 為準。
        """
        penalty = Decimal(0)
        for h in candidate.rule_hits:
            if h.severity == HitSeverity.WARNING:
                penalty += cls.WARNING_PENALTY
            elif h.severity == HitSeverity.FORBIDDEN:
                penalty += cls.FORBIDDEN_PENALTY
        value = base_score - penalty
        breakdown = {
            "base": base_score,
            "penalty": penalty,
        }
        return candidate.replace_score(RouteScore(value=value, breakdown=breakdown))

    @classmethod
    def evaluate_candidates_after_provider(
        cls,
        candidates: Sequence[RouteCandidate],
        *,
        base_scores: Sequence[Decimal],
        provider_empty_hint: Optional[str] = None,
    ) -> Tuple[List[RouteCandidate], Optional[NoRouteExplanation]]:
        """
        在 Provider 已寫入 **rule_hits** 後，對每筆候選套用例外路段、排序命中、計分，
        並判定是否存在至少一筆可行候選。

        責任：
        - 若全部候選在覆蓋後仍含 FORBIDDEN，回傳 `NoRouteExplanation`（不可回傳 None 訊息）。
        - **base_scores** 須與 **candidates** 等長，通常由距離／時間轉換而來。
        - **provider_empty_hint**：路網 Provider 未產生候選時之具體原因（例如 Overpass 504），優先於預設說明。
        """
        if len(base_scores) != len(candidates):
            raise RoutingInvalidValueError(
                "base_scores must align with candidates (same length)"
            )

        if not candidates:
            default_detail = (
                "The routing provider returned no candidates. "
                "Typical causes: Overpass ingest failed or no road ways in the request bbox, "
                "all ways excluded by forbidden prefilter (see MVP_ROUTING_FALLBACK_UNFILTERED_WHEN_ALL_BLOCKED), "
                "or MVP_ROUTING_REQUIRE_WAY_NAME_OR_REF excluding unnamed segments needed to connect the route."
            )
            detail = (provider_empty_hint or "").strip() or default_detail
            return [], NoRouteExplanation(
                code=NoRouteReasonCode.ROUTING_PROVIDER_EMPTY,
                message=f"No feasible route: {detail}",
            )

        processed: List[RouteCandidate] = []
        for c, base in zip(candidates, base_scores, strict=True):
            c2 = cls.apply_exception_road_overrides(c)
            sorted_hits = cls.sort_hits_forbidden_before_warning(c2.rule_hits)
            c2 = replace(c2, rule_hits=sorted_hits)
            c2 = cls.score_candidate(c2, base_score=base)
            processed.append(c2)

        feasible = [c for c in processed if not c.has_unsuppressed_forbidden_hit()]
        if feasible:
            return processed, None

        detail_parts = []
        for c in processed:
            forb = [h for h in c.rule_hits if h.severity == HitSeverity.FORBIDDEN]
            if forb:
                detail_parts.append(
                    f"rank {c.candidate_rank}: {len(forb)} forbidden hit(s)"
                )
        detail = "; ".join(detail_parts) if detail_parts else "No candidates returned."
        explanation = NoRouteExplanation(
            code=NoRouteReasonCode.ALL_CANDIDATES_FORBIDDEN,
            message=f"No feasible route: {detail}",
        )
        return processed, explanation

    @classmethod
    def best_feasible_candidate(
        cls, candidates: Iterable[RouteCandidate]
    ) -> Optional[RouteCandidate]:
        """
        自可行候選中挑選分數最高者（分數相同則候選排序較佳者在前）。

        責任：假設已通過 `evaluate_candidates_after_provider` 或同等流程。
        """
        feasible = [
            c
            for c in candidates
            if not c.has_unsuppressed_forbidden_hit() and c.score is not None
        ]
        if not feasible:
            return None
        return max(
            feasible,
            key=lambda c: (c.score.value if c.score else Decimal("-999999"), -c.candidate_rank),
        )
