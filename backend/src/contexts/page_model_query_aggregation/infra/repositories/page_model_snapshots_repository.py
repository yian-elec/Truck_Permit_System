"""
PageModelSnapshotsRepository — page_model.page_model_snapshots 讀寫。

責任：僅透過 `shared.core.db.connection.get_session` 取得 session，不自建 engine／session_factory。
"""

from __future__ import annotations

from typing import List
from uuid import UUID

from sqlalchemy import select

from shared.core.db.connection import get_session

from src.contexts.page_model_query_aggregation.infra.repositories._orm_detach import (
    detach_all,
    detach_optional,
)
from src.contexts.page_model_query_aggregation.infra.schema.page_model_snapshots import (
    PageModelSnapshots,
)


class PageModelSnapshotsRepository:
    """Page Model 快照表存取。"""

    def get_by_id(self, snapshot_id: UUID) -> PageModelSnapshots | None:
        with get_session() as session:
            row = session.get(PageModelSnapshots, snapshot_id)
            return detach_optional(session, row)

    def get_by_cache_key(self, cache_key: str) -> PageModelSnapshots | None:
        with get_session() as session:
            rows = list(
                session.scalars(
                    select(PageModelSnapshots)
                    .where(PageModelSnapshots.cache_key == cache_key)
                    .limit(1)
                ).all()
            )
            if not rows:
                return None
            return detach_optional(session, rows[0])

    def list_by_application_id(self, application_id: UUID) -> List[PageModelSnapshots]:
        with get_session() as session:
            rows = list(
                session.scalars(
                    select(PageModelSnapshots).where(
                        PageModelSnapshots.application_id == application_id
                    )
                ).all()
            )
            return detach_all(session, rows)

    def add(self, row: PageModelSnapshots) -> PageModelSnapshots:
        with get_session() as session:
            session.add(row)
            session.flush()
            session.refresh(row)
            return detach_optional(session, row)
