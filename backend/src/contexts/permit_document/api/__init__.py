"""
Permit_Document — HTTP API 套件。

責任：匯出 8.4 規格之路由器，供 **main** 掛載；業務規則在應用／領域層，本套件僅做
DTO 對應、依賴注入與統一回應包裝。
"""

from .routes import (
    permit_application_regenerate_router,
    permit_applicant_router,
    permit_resource_router,
)
from .stored_file_routes import router as permit_stored_file_router

__all__ = [
    "permit_applicant_router",
    "permit_resource_router",
    "permit_application_regenerate_router",
    "permit_stored_file_router",
]
