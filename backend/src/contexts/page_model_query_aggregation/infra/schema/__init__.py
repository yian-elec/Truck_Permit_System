"""
Page_Model_Query_Aggregation — infra schema（page_model.*）。

init_db 掃描本目錄 `*.py`（不含 __init__）並匯入模組，使 ORM 註冊至 Base.metadata。
"""

from .page_model_snapshots import PageModelSnapshots

__all__ = ["PageModelSnapshots"]
