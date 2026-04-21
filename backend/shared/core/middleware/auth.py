"""
auth.py - 認證中介軟體
驗證 JWT，攔截未授權請求
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Dict, Any
# 不在模組載入時導入 jwt_handler，而是在運行時動態獲取
from shared.errors.system_error.auth_error import (
    MissingTokenError,
    InvalidTokenError,
    ExpiredTokenError
)
from shared.core.logger.logger import logger


class AuthMiddleware(BaseHTTPMiddleware):
    """
    認證中介軟體
    
    功能：
    1. 驗證 Authorization header 是否存在
    2. 呼叫 jwt.verify() 驗證合法性
    3. 失敗 → 丟出對應的 JWT Error (401)
    4. 成功 → 把 payload 放到 request.state.user
    """
    
    def __init__(self, app, excluded_paths: list = None):
        """
        初始化認證中介軟體
        
        Args:
            app: FastAPI 應用程式實例
            excluded_paths: 不需要認證的路徑列表
        """
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/favicon.ico",
            "/api/v1/public",
            "/api/v1/auth/register",
            "/api/v1/auth/login",
            "/api/v1/auth/mfa/verify",
            "/api/v1/auth/refresh",
            # 許可證 PDF：POST download-url 已驗證身分；GET 由瀏覽器開啟，僅帶 expires+sig（HMAC），不可要求 JWT
            "/api/v1/stored-files",
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """
        中介軟體主要邏輯
        
        Args:
            request: FastAPI Request 物件
            call_next: 下一個中介軟體或路由處理器
            
        Returns:
            JSONResponse: 回應結果
        """
        # 瀏覽器跨域預檢（OPTIONS）不得要求 JWT；否則預檢 401 會讓實際請求無法帶上 Token。
        if request.method == "OPTIONS":
            return await call_next(request)

        # 檢查是否為排除的路徑
        if self._is_excluded_path(request.url.path):
            return await call_next(request)
        
        try:
            # 記錄 API 請求
            logger.api_info(
                method=request.method,
                path=request.url.path,
                **self._get_request_info(request)
            )
            
            # 驗證 JWT
            user_info = await self._authenticate(request)
            
            # 將使用者資訊存到 request.state
            request.state.user = user_info
            
            # 繼續處理請求
            response = await call_next(request)
            
            return response
            
        except (MissingTokenError, InvalidTokenError, ExpiredTokenError) as e:
            # 記錄認證錯誤
            logger.api_error(e.code, e.message)
            
            # 回傳統一的錯誤格式
            return JSONResponse(
                status_code=e.status_code,
                content=e.to_dict()
            )
        except Exception as e:
            # 記錄未預期的錯誤
            logger.error(f"Unexpected error in auth middleware: {str(e)}")
            
            # 回傳通用錯誤
            return JSONResponse(
                status_code=500,
                content={
                    "data": None,
                    "error": {
                        "code": "InternalServerError",
                        "message": "Internal server error",
                        "details": None
                    }
                }
            )
    
    def _is_excluded_path(self, path: str) -> bool:
        """
        檢查路徑是否在排除列表中
        
        Args:
            path: 請求路徑
            
        Returns:
            True 如果路徑被排除，False 如果需要認證
        """
        # 精確匹配或前綴匹配
        for excluded in self.excluded_paths:
            if path == excluded or path.startswith(excluded + "/"):
                return True
        return False
    
    async def _authenticate(self, request: Request) -> Dict[str, Any]:
        """
        執行認證邏輯
        
        Args:
            request: FastAPI Request 物件
            
        Returns:
            使用者資訊字典
            
        Raises:
            MissingTokenError: 缺少 Token
            InvalidTokenError: Token 無效
            ExpiredTokenError: Token 過期
        """
        # 創建新的 JWT handler 實例，確保使用最新的配置
        from shared.core.security.jwt.jwt_handler import JWTHandler
        jwt_handler = JWTHandler()
        
        # 取得 Authorization header
        authorization_header = request.headers.get("Authorization")
        
        # 提取 JWT Token
        token = jwt_handler.get_token_from_header(authorization_header)
        
        # 驗證 JWT Token
        payload = jwt_handler.verify(token)
        
        # 回傳使用者資訊
        return {
            "user_id": payload.get("sub"),
            "roles": payload.get("roles", []),
            "iat": payload.get("iat"),
            "exp": payload.get("exp")
        }
    
    def _get_request_info(self, request: Request) -> Dict[str, Any]:
        """
        取得請求相關資訊
        
        Args:
            request: FastAPI Request 物件
            
        Returns:
            請求資訊字典
        """
        info = {}
        
        # 取得客戶端 IP
        if hasattr(request, "client") and request.client:
            info["client_ip"] = request.client.host
        
        # 取得 User-Agent
        user_agent = request.headers.get("User-Agent")
        if user_agent:
            info["user_agent"] = user_agent[:100]  # 限制長度
        
        return info

