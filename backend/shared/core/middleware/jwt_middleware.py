"""
jwt_middleware.py - JWT 認證中介軟體
處理跨 context 的 JWT 認證邏輯
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from typing import Callable, Dict, Any, List, Optional
import re

# 不在模組載入時導入 jwt_handler，而是在運行時動態獲取
from shared.errors.system_error.auth_error import (
    MissingTokenError,
    InvalidTokenError,
    ExpiredTokenError
)
from shared.core.logger.logger import logger


class JWTMiddleware(BaseHTTPMiddleware):
    """
    JWT 認證中介軟體
    
    功能：
    1. 處理跨 context 的 JWT 認證
    2. 驗證 Authorization header 中的 JWT token
    3. 將用戶資訊注入到 request.state
    4. 支援多種認證策略
    """
    
    def __init__(self, app, excluded_paths: List[str] = None, require_auth_paths: List[str] = None):
        """
        初始化 JWT 中介軟體
        
        Args:
            app: FastAPI 應用程式實例
            excluded_paths: 不需要認證的路徑列表
            require_auth_paths: 需要認證的路徑列表（如果為空，則所有路徑都需要認證）
        """
        super().__init__(app)
        
        # 預設排除的路徑
        self.excluded_paths = excluded_paths or [
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
        
        # 需要認證的路徑（如果指定）
        self.require_auth_paths = require_auth_paths or []
    
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """
        處理請求，執行 JWT 認證
        
        Args:
            request: FastAPI Request 物件
            call_next: 下一個中介軟體或路由處理器
            
        Returns:
            JSONResponse: 回應結果
        """
        # 檢查是否為排除的路徑
        if self._is_excluded_path(request.url.path):
            return await call_next(request)
        
        # 檢查是否需要認證
        if self._requires_auth(request.url.path):
            try:
                # 記錄 API 請求
                logger.api_info(
                    method=request.method,
                    path=request.url.path,
                    **self._get_request_info(request)
                )
                
                # 執行 JWT 認證
                user_info = await self._authenticate(request)
                
                # 將用戶資訊注入到 request.state
                request.state.user = user_info
                request.state.user_id = user_info.get("user_id")
                request.state.user_roles = user_info.get("roles", [])
                request.state.jwt_payload = user_info
                
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
                logger.error(f"Unexpected error in JWT middleware: {str(e)}")
                
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
        
        return await call_next(request)
    
    def _is_excluded_path(self, path: str) -> bool:
        """
        檢查路徑是否在排除列表中
        
        Args:
            path: 請求路徑
            
        Returns:
            True 如果路徑被排除，False 如果需要認證
        """
        for excluded in self.excluded_paths:
            if path == excluded or path.startswith(excluded + "/"):
                return True
        return False
    
    def _requires_auth(self, path: str) -> bool:
        """
        檢查路徑是否需要認證
        
        Args:
            path: 請求路徑
            
        Returns:
            True 如果路徑需要認證，False 如果不需要
        """
        # 如果指定了需要認證的路徑，則只對這些路徑進行認證
        if self.require_auth_paths:
            for auth_path in self.require_auth_paths:
                if path == auth_path or path.startswith(auth_path + "/"):
                    return True
            return False
        
        # 如果沒有指定需要認證的路徑，則所有路徑都需要認證（除了排除的路徑）
        return True
    
    async def _authenticate(self, request: Request) -> Dict[str, Any]:
        """
        執行 JWT 認證邏輯
        
        Args:
            request: FastAPI Request 物件
            
        Returns:
            使用者資訊字典
            
        Raises:
            MissingTokenError: 缺少 Token
            InvalidTokenError: Token 無效
            ExpiredTokenError: Token 過期
        """
        # 取得 Authorization header
        authorization_header = request.headers.get("Authorization")
        
        # 提取 JWT Token
        token = self._extract_token(authorization_header)
        if not token:
            raise MissingTokenError("Missing Authorization header")
        
        # 創建新的 JWT handler 實例，確保使用最新的配置
        from shared.core.security.jwt.jwt_handler import JWTHandler
        jwt_handler = JWTHandler()
        
        # 驗證 JWT Token
        payload = jwt_handler.verify(token)
        
        # 回傳使用者資訊
        return {
            "user_id": payload.get("sub"),
            "roles": payload.get("roles", []),
            "iat": payload.get("iat"),
            "exp": payload.get("exp")
        }
    
    def _extract_token(self, auth_header: Optional[str]) -> Optional[str]:
        """
        從 Authorization header 中提取 JWT token
        
        Args:
            auth_header: Authorization header 值
            
        Returns:
            JWT token 字串，如果無法提取則返回 None
        """
        if not auth_header:
            return None
        
        # 支援 "Bearer <token>" 格式
        match = re.match(r"Bearer\s+(.+)", auth_header)
        if match:
            return match.group(1)
        
        # 也支援直接傳入 token（用於 Swagger UI）
        if auth_header and not auth_header.startswith("Bearer"):
            return auth_header
        
        return None
    
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
