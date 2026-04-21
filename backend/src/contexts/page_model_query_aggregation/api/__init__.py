"""
Page_Model_Query_Aggregation — API 層匯出。

責任：提供三組 FastAPI Router（申請人／審查／管理），於 `main.py` 註冊。
"""

from .routes import (
    page_model_admin_router,
    page_model_applicant_router,
    page_model_review_router,
)

__all__ = [
    "page_model_applicant_router",
    "page_model_review_router",
    "page_model_admin_router",
]
