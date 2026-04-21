"""
Page_Model_Query_Aggregation — Infrastructure。

責任：ORM schema、以 `shared.core.db.connection.get_session` 存取之 repositories、seed 資料；
`page_model_infra_bootstrap` 提供僅限本 schema 之建表／seed／自癒（不依賴全專案 init 成功）。
"""

from .page_model_infra_bootstrap import (
    ensure_page_model_schema_and_tables,
    reset_page_model_schema_for_recovery,
    seed_page_model_snapshots_if_empty,
)

__all__ = [
    "ensure_page_model_schema_and_tables",
    "seed_page_model_snapshots_if_empty",
    "reset_page_model_schema_for_recovery",
]
