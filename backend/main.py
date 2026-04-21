"""
main.py - FastAPI 應用程式主入口
整合所有 API 路由和中介軟體
"""

import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 載入配置
from shared.core.config import settings

# 導入所有 schema 以確保外鍵引用正確解析
from src.contexts.integration_operations.infra.schema import (  # noqa: F401
    AuditLogs,
    ImportJobs,
    NotificationJobs,
    OcrJobs,
    OcrResults,
)
from src.contexts.application.infra.schema import (  # noqa: F401
    ApplicantProfiles,
    Applications,
    Attachments,
    Checklists,
    CompanyProfiles,
    StatusHistories,
    StoredFiles,
    Vehicles,
)
from src.contexts.routing_restriction.infra.schema import (  # noqa: F401
    MapLayers,
    OfficerRouteOverrides,
    RestrictionRules,
    RouteCandidates,
    RoutePlans,
    RouteRequests,
    RouteRuleHits,
    RouteSegments,
    RuleGeometries,
    RuleTimeWindows,
)
from src.contexts.review_decision.infra.schema import (  # noqa: F401
    Decisions,
    ReviewComments,
    ReviewTasks,
    SupplementItems,
    SupplementRequests,
)
from src.contexts.permit_document.infra.schema import (  # noqa: F401
    CertificateAccessLogs,
    DocumentJobs,
    Documents,
    Permits,
)
from src.contexts.page_model_query_aggregation.infra.schema import (  # noqa: F401
    PageModelSnapshots,
)
from src.contexts.iam.infra.schema import (  # noqa: F401
    MfaChallenges,
    Permissions,
    RoleAssignments,
    RolePermissions,
    Roles,
    Sessions,
    Users,
)


@asynccontextmanager
async def _app_lifespan(_app: FastAPI):
    """
    建立資料庫／資料表並載入 seed。
    掛在 lifespan 上，以便 `uvicorn main:app` 與 `python main.py` 都會執行
    （僅在 __main__ 內呼叫 init_db 時，CLI 啟動會略過建表導致 iam.users 不存在）。
    """
    from shared.core.db.init_db import init_db
    from shared.core.logger.logger import logger

    logger.db_info("Starting database initialization on application startup...")
    ok = init_db()
    if not ok:
        msg = "Database initialization failed (init_db returned False). Check PostgreSQL and settings."
        logger.db_error(msg)
        raise RuntimeError(msg)
    logger.db_info("Database initialization completed on startup")
    yield


# 建立 FastAPI 應用程式
app = FastAPI(
    lifespan=_app_lifespan,
    title=settings.api.title,
    description=settings.api.description,
    version=settings.api.version_info,
    docs_url=settings.api.docs_url,
    redoc_url=settings.api.redoc_url,
    openapi_tags=[
        {
            "name": "作業整合（Ops）",
            "description": "Integration_Operations：OCR／通知／匯入作業與稽核紀錄之唯讀查詢",
        },
        {
            "name": "重型貨車通行證（公開）",
            "description": "Application：公開服務說明、必備文件、條款摘要與受理資訊（無需登入）",
        },
        {
            "name": "重型貨車通行證（申請人）",
            "description": "Application：申請人案件草稿、車輛、附件、送件與補件（需 JWT）",
        },
        {
            "name": "路線與限制（申請人）",
            "description": "Routing_Restriction：路線申請、預覽與重新規劃（需 JWT）",
        },
        {
            "name": "路線與限制（審查）",
            "description": "Routing_Restriction：審查端路線方案、選線、改線與規則命中（需 JWT）",
        },
        {
            "name": "路線與限制（管理）",
            "description": "Routing_Restriction：限制規則、圖層與 KML 匯入（需 JWT）",
        },
        {
            "name": "審查與決策",
            "description": "Review_Decision：審查任務、審核頁、補件、核准／駁回與稽核軌跡（需 JWT）",
        },
        {
            "name": "許可證與文件（申請人）",
            "description": "Permit_Document：申請人查詢許可摘要與文件下載 URL（需 JWT）",
        },
        {
            "name": "許可證與文件（資源）",
            "description": "Permit_Document：依許可識別查詢、列文件、簽發下載鏈結（需 JWT）",
        },
        {
            "name": "許可證與文件（申請／補產）",
            "description": "Permit_Document：請求重產許可相關文件（需 JWT）",
        },
        {
            "name": "畫面 Page Model（申請人）",
            "description": "Page_Model_Query_Aggregation：申請人首頁與案件編輯器聚合 read model（需 JWT）",
        },
        {
            "name": "畫面 Page Model（審查）",
            "description": "Page_Model_Query_Aggregation：審查員單案審查頁聚合 read model（需 JWT）",
        },
        {
            "name": "畫面 Page Model（管理）",
            "description": "Page_Model_Query_Aggregation：管理者儀表板聚合 read model（需 JWT）",
        },
        {
            "name": "IAM 認證與授權",
            "description": "IAM：註冊、登入、MFA、工作階段、自身資料／權限與管理員角色指派（部分端點需 JWT）",
        },
    ],
)

# 添加 JWT 認證配置到 OpenAPI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # 添加 JWT 認證配置
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "請輸入 JWT token，Swagger UI 會自動添加 'Bearer ' 前綴"
        }
    }
    
    # 添加全局安全配置
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    # 添加標籤配置
    openapi_schema["tags"] = [
        {
            "name": "作業整合（Ops）",
            "description": "Integration_Operations：OCR／通知／匯入作業與稽核紀錄之唯讀查詢",
        },
        {
            "name": "重型貨車通行證（公開）",
            "description": "Application：公開服務說明、必備文件、條款摘要與受理資訊（無需登入）",
        },
        {
            "name": "重型貨車通行證（申請人）",
            "description": "Application：申請人案件草稿、車輛、附件、送件與補件（需 JWT）",
        },
        {
            "name": "路線與限制（申請人）",
            "description": "Routing_Restriction：路線申請、預覽與重新規劃（需 JWT）",
        },
        {
            "name": "路線與限制（審查）",
            "description": "Routing_Restriction：審查端路線方案、選線、改線與規則命中（需 JWT）",
        },
        {
            "name": "路線與限制（管理）",
            "description": "Routing_Restriction：限制規則、圖層與 KML 匯入（需 JWT）",
        },
        {
            "name": "審查與決策",
            "description": "Review_Decision：審查任務、審核頁、補件、核准／駁回與稽核軌跡（需 JWT）",
        },
        {
            "name": "許可證與文件（申請人）",
            "description": "Permit_Document：申請人查詢許可摘要與文件下載 URL（需 JWT）",
        },
        {
            "name": "許可證與文件（資源）",
            "description": "Permit_Document：依許可識別查詢、列文件、簽發下載鏈結（需 JWT）",
        },
        {
            "name": "許可證與文件（申請／補產）",
            "description": "Permit_Document：請求重產許可相關文件（需 JWT）",
        },
        {
            "name": "畫面 Page Model（申請人）",
            "description": "Page_Model_Query_Aggregation：申請人首頁與案件編輯器聚合 read model（需 JWT）",
        },
        {
            "name": "畫面 Page Model（審查）",
            "description": "Page_Model_Query_Aggregation：審查員單案審查頁聚合 read model（需 JWT）",
        },
        {
            "name": "畫面 Page Model（管理）",
            "description": "Page_Model_Query_Aggregation：管理者儀表板聚合 read model（需 JWT）",
        },
        {
            "name": "IAM 認證與授權",
            "description": "IAM：註冊、登入、MFA、工作階段、自身資料／權限與管理員角色指派（部分端點需 JWT）",
        },
    ]
    
    # 為需要認證的端點添加安全要求
    protected_paths = [
        "/api/v1/ops",
        "/api/v1/applicant/applications",
        "/api/v1/applicant/pages",
        "/api/v1/review/",
        "/api/v1/admin",
        "/api/v1/permits",
        "/api/v1/applications/",
        "/api/v1/auth/me",
        "/api/v1/auth/me/permissions",
        "/api/v1/auth/logout",
    ]
    
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            # 檢查是否為需要認證的端點
            if any(protected_path in path for protected_path in protected_paths):
                openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# 中介層順序：後加入者在外層、請求先經過。
# CORS 必須在最外層，否則瀏覽器對跨域的 OPTIONS 預檢會先被 AuthMiddleware 回 401，
# 回應沒有 Access-Control-Allow-Origin，控制台會顯示 CORS 錯誤。
from shared.core.middleware.auth import AuthMiddleware

app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.cors_origins,
    allow_credentials=True,
    allow_methods=settings.security.cors_methods,
    allow_headers=settings.security.cors_headers,
)

# 全域異常處理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全域異常處理器"""
    return JSONResponse(
        status_code=500,
        content={
            "data": None,
            "error": {
                "code": "InternalServerError",
                "message": "Internal server error"
            }
        }
    )

# 健康檢查端點
@app.get(
    "/health",
    summary="健康檢查",
    description="檢查 API 服務是否正常運行",
    response_description="返回 API 服務狀態",
    responses={
        200: {
            "description": "服務正常",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "status": "healthy",
                            "message": "Truck_Permit_System API is running"
                        },
                        "error": None
                    }
                }
            }
        }
    }
)
async def health_check():
    """
    健康檢查端點
    
    用於檢查 API 服務是否正常運行，通常用於負載均衡器或監控系統。
    
    返回服務狀態和運行訊息。
    """
    return {
        "data": {
            "status": "healthy",
            "message": "Truck_Permit_System API is running"
        },
        "error": None
    }

from src.contexts.integration_operations.api.routes import router as ops_router
from src.contexts.application.api import (
    applicant_applications_router,
    public_heavy_truck_router,
)
from src.contexts.review_decision.api import review_decision_router
from src.contexts.routing_restriction.api import (
    routing_admin_router,
    routing_applicant_router,
    routing_review_router,
)
from src.contexts.permit_document.api import (
    permit_application_regenerate_router,
    permit_applicant_router,
    permit_resource_router,
    permit_stored_file_router,
)
from src.contexts.page_model_query_aggregation.api import (
    page_model_admin_router,
    page_model_applicant_router,
    page_model_review_router,
)
from src.contexts.iam.api import iam_router

app.include_router(ops_router)
app.include_router(public_heavy_truck_router)
app.include_router(applicant_applications_router)
app.include_router(routing_applicant_router)
app.include_router(review_decision_router)
app.include_router(routing_review_router)
app.include_router(routing_admin_router)
app.include_router(permit_stored_file_router)
app.include_router(permit_applicant_router)
app.include_router(permit_resource_router)
app.include_router(permit_application_regenerate_router)
app.include_router(page_model_applicant_router)
app.include_router(page_model_review_router)
app.include_router(page_model_admin_router)
app.include_router(iam_router)

# 根路徑
@app.get(
    "/",
    summary="API 根路徑",
    description="返回 API 基本資訊和文檔連結",
    response_description="返回 API 歡迎訊息和相關連結",
    responses={
        200: {
            "description": "成功返回 API 資訊",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "message": "Welcome to Truck_Permit_System API",
                            "version": "1.0.0",
                            "docs": "/docs"
                        },
                        "error": None
                    }
                }
            }
        }
    }
)
async def root():
    """
    API 根路徑
    
    返回 API 的基本資訊，包括版本號和文檔連結。
    
    提供 Swagger UI 文檔的連結。
    """
    return {
        "data": {
            "message": "Welcome to Truck_Permit_System API",
            "version": "1.0.0",
            "docs": "/docs"
        },
        "error": None
    }

if __name__ == "__main__":
    import uvicorn

    # 資料庫初始化於 FastAPI lifespan（_app_lifespan）內執行，無須在此重複呼叫
    
    # 啟動伺服器
    print("\n🚀 啟動 Truck_Permit_System API 伺服器...")
    print(f"📖 API 文件: {settings.api.full_docs_url}")
    print(f"🔍 ReDoc: http://{settings.api.host}:{settings.api.port}{settings.api.redoc_url}")
    print(f"❤️  健康檢查: http://{settings.api.host}:{settings.api.port}{settings.api.health_check_url}")
    
    uvicorn.run(
        "main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=True,
        log_level=settings.log_level.lower()
    )