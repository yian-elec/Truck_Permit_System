"""
Application context — API 層。

匯出公開服務與申請人案件兩組路由器，於 `main.py` 掛載；路由僅依賴 App 層 DTO 與服務。
"""

from .routes import applicant_applications_router, public_heavy_truck_router

__all__ = [
    "public_heavy_truck_router",
    "applicant_applications_router",
]
