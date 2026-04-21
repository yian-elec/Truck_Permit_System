"""
Review_Decision Domain 測試共用 fixture。

責任：提供固定時間與 UUID，避免測試依賴真實時鐘或隨機性；不包含任何 I/O。
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest


@pytest.fixture
def fixed_now() -> datetime:
    """固定 UTC 時間，供聚合狀態轉移斷言 updated_at。"""
    return datetime(2026, 4, 7, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def actor_user_id():
    """決策者／評論者 UUID。"""
    return uuid4()
