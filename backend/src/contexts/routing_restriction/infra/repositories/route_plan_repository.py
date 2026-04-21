"""
RoutePlanRepository — routing.route_plans 及其候選、路段、規則命中之讀寫。

責任：單一交易內寫入完整規劃聚合；讀取時還原領域 RoutePlan（含巢狀候選／路段／命中）。
"""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from geoalchemy2.elements import WKTElement
from sqlalchemy import select, text

from shared.core.db.connection import get_session

from src.contexts.routing_restriction.domain.entities.route_candidate import RouteCandidate
from src.contexts.routing_restriction.domain.entities.route_plan import RoutePlan
from src.contexts.routing_restriction.domain.entities.route_segment import RouteSegment
from src.contexts.routing_restriction.domain.value_objects.no_route_explanation import (
    NoRouteExplanation,
)
from src.contexts.routing_restriction.domain.value_objects.route_geometry import RouteGeometry
from src.contexts.routing_restriction.domain.value_objects.route_score import RouteScore
from src.contexts.routing_restriction.domain.value_objects.rule_hit import RuleHit
from src.contexts.routing_restriction.domain.value_objects.routing_enums import (
    HitSeverity,
    NoRouteReasonCode,
    RoutePlanStatus,
    RuleType,
)
from src.contexts.routing_restriction.infra.repositories.geometry_wkt import (
    parse_linestring_wkt,
    route_geometry_linestring_to_wkt,
)
from src.contexts.routing_restriction.infra.schema.route_candidates import RouteCandidates
from src.contexts.routing_restriction.infra.schema.route_plans import RoutePlans
from src.contexts.routing_restriction.infra.schema.route_rule_hits import RouteRuleHits
from src.contexts.routing_restriction.infra.schema.route_segments import RouteSegments
from src.contexts.routing_restriction.infra.schema.restriction_rules import RestrictionRules


def _line_wkt_element(g: RouteGeometry) -> WKTElement:
    return WKTElement(route_geometry_linestring_to_wkt(g), srid=4326)


def _candidate_line_wkt(session, candidate_id: UUID) -> RouteGeometry:
    wkt = session.execute(
        text("SELECT ST_AsText(geom) FROM routing.route_candidates WHERE candidate_id = :id"),
        {"id": candidate_id},
    ).scalar()
    if not wkt:
        raise ValueError(f"Missing geometry for candidate {candidate_id}")
    return parse_linestring_wkt(wkt)


def _segment_line_wkt(session, segment_id: UUID) -> RouteGeometry:
    wkt = session.execute(
        text("SELECT ST_AsText(geom) FROM routing.route_segments WHERE segment_id = :id"),
        {"id": segment_id},
    ).scalar()
    if not wkt:
        raise ValueError(f"Missing geometry for segment {segment_id}")
    return parse_linestring_wkt(wkt)


def _load_rule_types(session, rule_ids: List[UUID]) -> Dict[UUID, RuleType]:
    if not rule_ids:
        return {}
    rows = session.scalars(
        select(RestrictionRules).where(RestrictionRules.rule_id.in_(rule_ids))
    ).all()
    return {r.rule_id: RuleType(r.rule_type) for r in rows}


def _row_to_domain_plan(session, row: RoutePlans) -> RoutePlan:
    plan_id = row.route_plan_id
    cand_rows = session.scalars(
        select(RouteCandidates)
        .where(RouteCandidates.route_plan_id == plan_id)
        .order_by(RouteCandidates.candidate_rank)
    ).all()

    candidates: List[RouteCandidate] = []
    for cr in cand_rows:
        line_g = _candidate_line_wkt(session, cr.candidate_id)
        seg_rows = session.scalars(
            select(RouteSegments)
            .where(RouteSegments.candidate_id == cr.candidate_id)
            .order_by(RouteSegments.seq_no)
        ).all()
        segments: List[RouteSegment] = []
        for sr in seg_rows:
            sg = _segment_line_wkt(session, sr.segment_id)
            segments.append(
                RouteSegment(
                    segment_id=sr.segment_id,
                    candidate_id=sr.candidate_id,
                    seq_no=sr.seq_no,
                    distance_m=sr.distance_m,
                    duration_s=sr.duration_s,
                    geometry=sg,
                    road_name=sr.road_name,
                    instruction_text=sr.instruction_text,
                    is_exception_road=bool(sr.is_exception_road),
                    created_at=sr.created_at,
                )
            )
        hit_rows = session.scalars(
            select(RouteRuleHits).where(RouteRuleHits.candidate_id == cr.candidate_id)
        ).all()
        rule_ids = list({h.rule_id for h in hit_rows})
        rt_map = _load_rule_types(session, rule_ids)
        seg_id_to_idx = {s.segment_id: i for i, s in enumerate(segments)}
        hits: List[RuleHit] = []
        for h in hit_rows:
            seg_idx: Optional[int] = None
            if h.segment_id is not None and h.segment_id in seg_id_to_idx:
                seg_idx = seg_id_to_idx[h.segment_id]
            hits.append(
                RuleHit(
                    rule_id=h.rule_id,
                    rule_type=rt_map.get(h.rule_id, RuleType.FORBIDDEN_ZONE),
                    severity=HitSeverity(h.hit_type),
                    segment_index=seg_idx,
                    detail_text=h.detail_text,
                )
            )
        score_vo = RouteScore(value=Decimal(str(cr.score)))
        ar_seq = cr.area_road_sequence
        if ar_seq is not None and not isinstance(ar_seq, list):
            ar_seq = list(ar_seq) if ar_seq else None
        candidates.append(
            RouteCandidate(
                candidate_id=cr.candidate_id,
                route_plan_id=cr.route_plan_id,
                candidate_rank=cr.candidate_rank,
                distance_m=cr.distance_m,
                duration_s=cr.duration_s,
                line_geometry=line_g,
                score=score_vo,
                summary_text=cr.summary_text,
                area_road_sequence=ar_seq,
                segments=segments,
                rule_hits=hits,
                created_at=cr.created_at,
            )
        )

    no_route: Optional[NoRouteExplanation] = None
    if row.no_route_message:
        try:
            code = (
                NoRouteReasonCode(row.no_route_code)
                if row.no_route_code
                else NoRouteReasonCode.UNKNOWN
            )
        except ValueError:
            code = NoRouteReasonCode.UNKNOWN
        no_route = NoRouteExplanation(code=code, message=row.no_route_message)

    return RoutePlan(
        route_plan_id=row.route_plan_id,
        application_id=row.application_id,
        route_request_id=row.route_request_id,
        status=RoutePlanStatus(row.status),
        planning_version=row.planning_version,
        map_version=row.map_version,
        candidates=candidates,
        selected_candidate_id=row.selected_candidate_id,
        no_route_explanation=no_route,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class RoutePlanRepository:
    """路線規劃聚合之讀寫。"""

    def save_full_plan(self, plan: RoutePlan) -> None:
        """
        寫入計畫主檔及所有候選、路段、規則命中。

        責任：假設為新計畫（新 route_plan_id）；若重複主鍵則由資料庫約束失敗。
        """
        with get_session() as session:
            rp = RoutePlans(
                route_plan_id=plan.route_plan_id,
                application_id=plan.application_id,
                route_request_id=plan.route_request_id,
                status=plan.status.value,
                selected_candidate_id=plan.selected_candidate_id,
                planning_version=plan.planning_version,
                map_version=plan.map_version,
                no_route_code=plan.no_route_explanation.code.value if plan.no_route_explanation else None,
                no_route_message=plan.no_route_explanation.message if plan.no_route_explanation else None,
                created_at=plan.created_at,
                updated_at=plan.updated_at,
            )
            session.add(rp)
            session.flush()

            for c in plan.candidates:
                if c.score is None:
                    raise ValueError("Candidate must have score before persistence")
                rc = RouteCandidates(
                    candidate_id=c.candidate_id,
                    route_plan_id=c.route_plan_id,
                    candidate_rank=c.candidate_rank,
                    distance_m=c.distance_m,
                    duration_s=c.duration_s,
                    score=c.score.value,
                    summary_text=c.summary_text,
                    area_road_sequence=c.area_road_sequence,
                    geom=_line_wkt_element(c.line_geometry),
                    created_at=c.created_at,
                )
                session.add(rc)
                for s in c.segments:
                    rs = RouteSegments(
                        segment_id=s.segment_id,
                        candidate_id=s.candidate_id,
                        seq_no=s.seq_no,
                        road_name=s.road_name,
                        distance_m=s.distance_m,
                        duration_s=s.duration_s,
                        geom=_line_wkt_element(s.geometry),
                        instruction_text=s.instruction_text,
                        is_exception_road=s.is_exception_road,
                        created_at=s.created_at,
                    )
                    session.add(rs)
                for h in c.rule_hits:
                    seg_uuid: Optional[UUID] = None
                    if h.segment_index is not None and 0 <= h.segment_index < len(c.segments):
                        seg_uuid = c.segments[h.segment_index].segment_id
                    rh = RouteRuleHits(
                        rule_hit_id=uuid4(),
                        candidate_id=c.candidate_id,
                        rule_id=h.rule_id,
                        hit_type=h.severity.value,
                        segment_id=seg_uuid,
                        detail_text=h.detail_text,
                    )
                    session.add(rh)

    def find_by_id(self, route_plan_id: UUID) -> Optional[RoutePlan]:
        with get_session() as session:
            row = session.get(RoutePlans, route_plan_id)
            if row is None:
                return None
            return _row_to_domain_plan(session, row)

    def find_latest_by_application_id(self, application_id: UUID) -> Optional[RoutePlan]:
        with get_session() as session:
            stmt = (
                select(RoutePlans)
                .where(RoutePlans.application_id == application_id)
                .order_by(RoutePlans.created_at.desc())
                .limit(1)
            )
            row = session.scalars(stmt).first()
            if row is None:
                return None
            return _row_to_domain_plan(session, row)

    def update_plan_header(self, plan: RoutePlan) -> None:
        """僅更新計畫主檔；供 UC-ROUTE-04／05。"""
        with get_session() as session:
            row = session.get(RoutePlans, plan.route_plan_id)
            if row is None:
                raise LookupError(f"route_plan not found: {plan.route_plan_id}")
            row.status = plan.status.value
            row.selected_candidate_id = plan.selected_candidate_id
            row.planning_version = plan.planning_version
            row.map_version = plan.map_version
            row.no_route_code = (
                plan.no_route_explanation.code.value if plan.no_route_explanation else None
            )
            row.no_route_message = (
                plan.no_route_explanation.message if plan.no_route_explanation else None
            )
            row.updated_at = plan.updated_at
