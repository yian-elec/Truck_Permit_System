"""
Application context — 持久化與讀模型埠（Domain 定義，Infra 實作）。

責任：`ApplicationRepository` 負責聚合之載入／儲存；`ApplicationReadModelQuery` 負責唯讀查詢，
兩者均為依賴反轉邊界，不包含任何 ORM 或 SQL。
"""

from .application_read_model_query import ApplicationReadModelQuery
from .application_repository import ApplicationRepository

__all__ = ["ApplicationRepository", "ApplicationReadModelQuery"]
