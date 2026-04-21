"""
RestrictionRulesRepository — routing.restriction_rules 讀寫（管理端／規劃參考）。

責任：僅資料存取；規則業務不變式由領域與 App 服務把關。
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select

from shared.core.db.connection import get_session

from src.contexts.routing_restriction.infra.schema.restriction_rules import RestrictionRules


def _expunge_row(session, row: RestrictionRules | None) -> RestrictionRules | None:
    """commit 前自 Session 卸載，避免 expire_on_commit 導致脫離 Session 後無法讀欄位。"""
    if row is None:
        return None
    session.expunge(row)
    return row


def _expunge_rows(session, rows: List[RestrictionRules]) -> List[RestrictionRules]:
    for obj in rows:
        session.expunge(obj)
    return rows


class RestrictionRulesRepository:
    """限制規則主檔 CRUD 之最小集合。"""

    def list_rules(
        self,
        *,
        layer_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        limit: int = 500,
    ) -> List[RestrictionRules]:
        with get_session() as session:
            stmt = select(RestrictionRules).order_by(RestrictionRules.priority, RestrictionRules.rule_name)
            if layer_id is not None:
                stmt = stmt.where(RestrictionRules.layer_id == layer_id)
            if is_active is not None:
                stmt = stmt.where(RestrictionRules.is_active.is_(is_active))
            stmt = stmt.limit(limit)
            rows = list(session.scalars(stmt).all())
            return _expunge_rows(session, rows)

    def get_by_id(self, rule_id: UUID) -> Optional[RestrictionRules]:
        with get_session() as session:
            row = session.get(RestrictionRules, rule_id)
            return _expunge_row(session, row)

    def save_standalone(self, row: RestrictionRules) -> None:
        """新增或更新單筆規則（依主鍵 upsert）。"""
        with get_session() as session:
            session.merge(row)

    def patch_fields(
        self,
        rule_id: UUID,
        *,
        rule_name: Optional[str] = None,
        weight_limit_ton: Optional[Decimal] = None,
        priority: Optional[int] = None,
        time_rule_text: Optional[str] = None,
        effective_from: Optional[date] = None,
        effective_to: Optional[date] = None,
    ) -> Optional[RestrictionRules]:
        """部分更新；若不存在回傳 None。"""
        with get_session() as session:
            row = session.get(RestrictionRules, rule_id)
            if row is None:
                return None
            if rule_name is not None:
                row.rule_name = rule_name
            if weight_limit_ton is not None:
                row.weight_limit_ton = weight_limit_ton
            if priority is not None:
                row.priority = priority
            if time_rule_text is not None:
                row.time_rule_text = time_rule_text
            if effective_from is not None:
                row.effective_from = effective_from
            if effective_to is not None:
                row.effective_to = effective_to
            session.flush()
            return _expunge_row(session, row)

    def set_active(self, rule_id: UUID, *, is_active: bool) -> Optional[RestrictionRules]:
        with get_session() as session:
            row = session.get(RestrictionRules, rule_id)
            if row is None:
                return None
            row.is_active = is_active
            session.flush()
            return _expunge_row(session, row)
