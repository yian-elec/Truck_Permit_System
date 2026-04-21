"""
mfa_challenges_repository — iam.mfa_challenges 讀寫。

僅使用 `shared.core.db.connection.get_session`。
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from shared.core.db.connection import get_session

from src.contexts.iam.infra.repositories._orm_detach import detach_optional
from src.contexts.iam.infra.schema.mfa_challenges import MfaChallenges


class MfaChallengesRepository:
    """MFA 挑戰持久化。"""

    def get_by_challenge_id(self, challenge_id: UUID) -> Optional[MfaChallenges]:
        with get_session() as session:
            row = session.get(MfaChallenges, challenge_id)
            return detach_optional(session, row)

    def add(self, row: MfaChallenges) -> MfaChallenges:
        with get_session() as session:
            session.add(row)
            session.flush()
            session.refresh(row)
            return detach_optional(session, row)

    def update_verified_at(self, challenge_id: UUID, verified_at) -> None:
        with get_session() as session:
            row = session.get(MfaChallenges, challenge_id)
            if row is None:
                return
            row.verified_at = verified_at
