"""
route_plans — ORM 對應 routing.route_plans。
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared.core.db.connection import Base


class RoutePlans(Base):
    """路線規劃結果（含 planning／map 版本字串）。"""

    __tablename__ = "route_plans"
    __table_args__ = {"schema": "routing"}

    route_plan_id = Column(UUID(as_uuid=True), primary_key=True)
    application_id = Column(UUID(as_uuid=True), nullable=False)
    route_request_id = Column(
        UUID(as_uuid=True),
        ForeignKey("routing.route_requests.route_request_id"),
        nullable=False,
    )
    status = Column(String(30), nullable=False)
    # 不設 DB 層 FK：與 route_candidates.route_plan_id 形成循環參照；由 App 保證候選隸屬同一計畫。
    selected_candidate_id = Column(UUID(as_uuid=True), nullable=True)
    planning_version = Column(String(50), nullable=False)
    map_version = Column(String(50), nullable=False)
    # 無可行路線時之結構化原因（與領域 NoRouteExplanation 對齊；status=no_route 時建議填寫）
    no_route_code = Column(String(50), nullable=True)
    no_route_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
