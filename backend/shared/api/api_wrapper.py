"""
api_wrapper.py - API 回應包裝器
提供統一的 API 回應格式、錯誤處理和日誌記錄
"""

from typing import Any, Dict, Tuple, Optional
from fastapi import Request
from fastapi.responses import JSONResponse

from shared.errors.base_error.base_error import BaseError
from shared.errors.domain_error.domain_error import DomainError
from shared.errors.app_error.app_error import AppError
from shared.errors.system_error.system_error import SystemError
from shared.core.logger.logger import logger


class APIResponse:
    """
    API 回應類別
    
    統一回應格式：
    成功回應: {"data": {...}, "error": null}
    錯誤回應: {"data": null, "error": {"code": "ErrorCode", "message": "Error message"}}
    """
    
    def __init__(self, data: Any = None, error: Optional[Dict[str, str]] = None, status_code: int = 200):
        """
        初始化 API 回應
        
        Args:
            data: 回應資料
            error: 錯誤資訊
            status_code: HTTP 狀態碼
        """
        self.data = data
        self.error = error
        self.status_code = status_code
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "data": self.data,
            "error": self.error
        }
    
    def to_json_response(self) -> JSONResponse:
        """轉換為 FastAPI JSONResponse"""
        return JSONResponse(
            content=self.to_dict(),
            status_code=self.status_code
        )


def api_response(result: Any, request: Optional[Request] = None) -> Tuple[Dict[str, Any], int]:
    """
    API 回應包裝器
    
    統一回應格式：
    - 成功回應: {"data": {...}, "error": null}
    - 錯誤回應: {"data": null, "error": {"code": "ErrorCode", "message": "Error message"}}
    
    Args:
        result: Use Case 執行結果或異常
        request: FastAPI Request 物件（用於日誌記錄）
        
    Returns:
        Tuple[Dict[str, Any], int]: (回應內容, HTTP 狀態碼)
    """
    # 記錄 API 進入日誌
    if request:
        user_id = getattr(request.state, 'user_id', None)
        logger.api_info(
            method=request.method,
            path=request.url.path,
            user_id=str(user_id) if user_id else None
        )
    
    # 檢查 result 是否為異常
    if isinstance(result, BaseError):
        # 記錄錯誤日誌
        if request:
            logger.api_error(
                method=request.method,
                path=request.url.path,
                error_code=result.code,
                error_message=str(result)
            )
        
        # 錯誤回應
        response_data = {
            "data": None,
            "error": {
                "code": result.code,
                "message": result.message if hasattr(result, 'message') else str(result)
            }
        }
        
        return response_data, result.status_code
    
    elif isinstance(result, Exception):
        # 記錄未預期錯誤日誌
        if request:
            logger.api_error(
                method=request.method,
                path=request.url.path,
                error_code="InternalServerError",
                error_message=str(result)
            )
        
        # 未預期錯誤回應
        response_data = {
            "data": None,
            "error": {
                "code": "InternalServerError",
                "message": "Internal server error"
            }
        }
        
        return response_data, 500
    
    else:
        # 成功回應
        # 如果 result 是 Pydantic 模型，轉換為字典
        if hasattr(result, 'model_dump'):
            # Pydantic v2
            data = result.model_dump()
        elif hasattr(result, 'dict'):
            # Pydantic v1
            data = result.dict()
        else:
            # 其他類型直接使用
            data = result
            
        response_data = {
            "data": data,
            "error": None
        }
        
        return response_data, 200


def api_response_with_logging(result: Any, request: Request) -> JSONResponse:
    """
    帶日誌記錄的 API 回應包裝器（FastAPI 專用）
    
    Args:
        result: Use Case 執行結果或異常
        request: FastAPI Request 物件
        
    Returns:
        JSONResponse: FastAPI JSONResponse 物件
    """
    # 記錄 API 進入日誌
    user_id = getattr(request.state, 'user_id', None)
    logger.api_info(
        method=request.method,
        path=request.url.path,
        user_id=str(user_id) if user_id else None
    )
    
    # 檢查 result 是否為異常
    if isinstance(result, BaseError):
        # 記錄錯誤日誌
        logger.api_error(
            method=request.method,
            path=request.url.path,
            error_code=result.code,
            error_message=str(result)
        )
        
        # 錯誤回應
        response_data = {
            "data": None,
            "error": {
                "code": result.code,
                "message": result.message if hasattr(result, 'message') else str(result)
            }
        }
        
        return JSONResponse(content=response_data, status_code=result.status_code)
    
    elif isinstance(result, Exception):
        # 記錄未預期錯誤日誌
        logger.api_error(
            method=request.method,
            path=request.url.path,
            error_code="InternalServerError",
            error_message=str(result)
        )
        
        # 未預期錯誤回應
        response_data = {
            "data": None,
            "error": {
                "code": "InternalServerError",
                "message": "Internal server error"
            }
        }
        
        return JSONResponse(content=response_data, status_code=500)
    
    else:
        # 成功回應
        # 如果 result 是 Pydantic 模型，轉換為字典
        if hasattr(result, 'model_dump'):
            # Pydantic v2
            data = result.model_dump()
        elif hasattr(result, 'dict'):
            # Pydantic v1
            data = result.dict()
        else:
            # 其他類型直接使用
            data = result
            
        response_data = {
            "data": data,
            "error": None
        }
        
        return JSONResponse(content=response_data, status_code=200)


def handle_domain_error(error: DomainError, request: Optional[Request] = None) -> Tuple[Dict[str, Any], int]:
    """
    處理 Domain 層錯誤
    
    Args:
        error: Domain 錯誤
        request: FastAPI Request 物件
        
    Returns:
        Tuple[Dict[str, Any], int]: (回應內容, HTTP 狀態碼)
    """
    if request:
        logger.api_error(
            method=request.method,
            path=request.url.path,
            error_code=error.code,
            error_message=str(error)
        )
    
    response_data = {
        "data": None,
        "error": {
            "code": error.code,
            "message": str(error)
        }
    }
    
    return response_data, error.status_code


def handle_app_error(error: AppError, request: Optional[Request] = None) -> Tuple[Dict[str, Any], int]:
    """
    處理 App 層錯誤
    
    Args:
        error: App 錯誤
        request: FastAPI Request 物件
        
    Returns:
        Tuple[Dict[str, Any], int]: (回應內容, HTTP 狀態碼)
    """
    if request:
        logger.api_error(
            method=request.method,
            path=request.url.path,
            error_code=error.code,
            error_message=str(error)
        )
    
    response_data = {
        "data": None,
        "error": {
            "code": error.code,
            "message": str(error)
        }
    }
    
    return response_data, error.status_code


def handle_system_error(error: SystemError, request: Optional[Request] = None) -> Tuple[Dict[str, Any], int]:
    """
    處理 System 層錯誤
    
    Args:
        error: System 錯誤
        request: FastAPI Request 物件
        
    Returns:
        Tuple[Dict[str, Any], int]: (回應內容, HTTP 狀態碼)
    """
    if request:
        logger.api_error(
            method=request.method,
            path=request.url.path,
            error_code=error.code,
            error_message=str(error)
        )
    
    response_data = {
        "data": None,
        "error": {
            "code": error.code,
            "message": str(error)
        }
    }
    
    return response_data, error.status_code
