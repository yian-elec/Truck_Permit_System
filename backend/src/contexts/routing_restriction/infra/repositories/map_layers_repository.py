"""
MapLayersRepository — map_layers 讀取（Infra）。

責任：透過 `get_session` 查詢 `routing.map_layers`；不實作業務規則。
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from shared.core.db.connection import get_session

from src.contexts.routing_restriction.infra.schema.map_layers import MapLayers


def _expunge_layer(session: Session, row: MapLayers | None) -> MapLayers | None:
    if row is None:
        return None
    session.expunge(row)
    return row


def _exp_layers(session: Session, rows: List[MapLayers]) -> List[MapLayers]:
    for obj in rows:
        session.expunge(obj)
    return rows


class MapLayersRepository:
    """圖資 layer 資料存取；session 一律由 core/db 提供。"""

    def get_by_id(self, layer_id: UUID) -> MapLayers | None:
        with get_session() as session:
            row = session.query(MapLayers).filter_by(layer_id=layer_id).first()
            return _expunge_layer(session, row)

    def list_by_active(self, *, is_active: bool) -> List[MapLayers]:
        with get_session() as session:
            rows = (
                session.query(MapLayers)
                .filter(MapLayers.is_active.is_(is_active))
                .order_by(MapLayers.created_at.desc())
                .all()
            )
            return _exp_layers(session, list(rows))

    def save(self, session: Session, row: MapLayers) -> None:
        """
        於**外部已開啟**之 session 內儲存（供上層同一交易內組合多表寫入）。

        責任：不自行取得 session；若僅單表寫入可改用 `save_standalone`。
        """
        session.add(row)

    def save_standalone(self, row: MapLayers) -> None:
        """單表寫入：內部 `with get_session()` 並 commit。"""
        with get_session() as session:
            session.add(row)

    def get_latest_published_layer(self) -> MapLayers | None:
        """
        與 resolve_map_version_for_planning 相同條件：最新一筆已發布且啟用之 layer。
        """
        with get_session() as session:
            stmt = (
                select(MapLayers)
                .where(MapLayers.is_active.is_(True), MapLayers.published_at.isnot(None))
                .order_by(MapLayers.published_at.desc())
                .limit(1)
            )
            row = session.scalars(stmt).first()
            return _expunge_layer(session, row)

    def resolve_map_version_for_planning(self) -> str:
        """
        取得寫入 RoutePlan.map_version 用之版本字串。

        責任：優先使用「已發布且啟用」之 layer.version_no；否則取任一最新 layer；皆無則回傳固定字樣。
        """
        with get_session() as session:
            stmt_pub = (
                select(MapLayers)
                .where(MapLayers.is_active.is_(True), MapLayers.published_at.isnot(None))
                .order_by(MapLayers.published_at.desc())
                .limit(1)
            )
            row = session.scalars(stmt_pub).first()
            if row is not None:
                return row.version_no
            stmt_any = select(MapLayers).order_by(MapLayers.created_at.desc()).limit(1)
            row2 = session.scalars(stmt_any).first()
            if row2 is not None:
                return row2.version_no
            return "no_layer"

    def list_all_recent(self, *, limit: int = 200) -> List[MapLayers]:
        """依建立時間倒序列出 layer（管理端列表）。"""
        with get_session() as session:
            stmt = select(MapLayers).order_by(MapLayers.created_at.desc()).limit(limit)
            rows = list(session.scalars(stmt).all())
            return _exp_layers(session, rows)

    def publish_layer(self, layer_id: UUID) -> MapLayers | None:
        """將 layer 標為啟用並寫入發布時間。"""
        with get_session() as session:
            row = session.get(MapLayers, layer_id)
            if row is None:
                return None
            row.is_active = True
            row.published_at = datetime.now(timezone.utc)
            # 必須先 flush：若在 commit 前對「已修改」實體 expunge，UPDATE 可能不會寫入 DB，
            # 導致 API 回應仍用記憶體中的 True，但 GET 列表讀庫仍為未啟用。
            session.flush()
            return _expunge_layer(session, row)
