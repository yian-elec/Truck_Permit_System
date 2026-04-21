"""
與 PostgisSpatialRuleHitPort 共用：本次適用之 restriction_rules + rule_geometries。

第一版：`published layer` 內 active 規則 + effective 日期 + 車重；不讀 rule_time_windows。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Dict, List
from uuid import UUID

from sqlalchemy.orm import Session

from src.contexts.routing_restriction.domain.value_objects.vehicle_constraint import VehicleConstraint
from src.contexts.routing_restriction.infra.schema.restriction_rules import RestrictionRules
from src.contexts.routing_restriction.infra.schema.rule_geometries import RuleGeometries


def applies_restriction_rule_row(
    row: RestrictionRules,
    *,
    on_date: date,
    vehicle: VehicleConstraint,
) -> bool:
    """與 PostgisSpatialRuleHitPort._applies_rule_row 語意一致（不含 time windows）。"""
    if not row.is_active:
        return False
    if row.effective_from is not None and on_date < row.effective_from:
        return False
    if row.effective_to is not None and on_date > row.effective_to:
        return False
    wt = row.weight_limit_ton
    if wt is not None:
        lim = Decimal(str(wt)) if not isinstance(wt, Decimal) else wt
        if not vehicle.is_heavier_or_equal_than(lim):
            return False
    return True


@dataclass(frozen=True)
class ApplicableRulesContext:
    """已篩選之規則與依 rule_id 分組之幾何。"""

    layer_id: UUID
    applicable_rules: List[RestrictionRules]
    geoms_by_rule: Dict[UUID, List[RuleGeometries]]


def load_applicable_rules_context(
    session: Session,
    *,
    layer_id: UUID,
    vehicle: VehicleConstraint,
    departure_at: datetime | None,
) -> ApplicableRulesContext:
    """
    讀取 layer 內規則列，套用日期／車重，並載入對應 rule_geometries。
    """
    dep = departure_at if departure_at is not None else datetime.now(timezone.utc)
    on_date = dep.date()

    rule_rows = (
        session.query(RestrictionRules)
        .filter(
            RestrictionRules.layer_id == layer_id,
            RestrictionRules.is_active.is_(True),
        )
        .all()
    )
    applicable: List[RestrictionRules] = [
        r for r in rule_rows if applies_restriction_rule_row(r, on_date=on_date, vehicle=vehicle)
    ]
    if not applicable:
        return ApplicableRulesContext(layer_id=layer_id, applicable_rules=[], geoms_by_rule={})

    rule_ids = [r.rule_id for r in applicable]
    geom_rows = session.query(RuleGeometries).filter(RuleGeometries.rule_id.in_(rule_ids)).all()
    geoms_by_rule: Dict[UUID, List[RuleGeometries]] = {}
    for g in geom_rows:
        geoms_by_rule.setdefault(g.rule_id, []).append(g)

    return ApplicableRulesContext(
        layer_id=layer_id,
        applicable_rules=applicable,
        geoms_by_rule=geoms_by_rule,
    )
