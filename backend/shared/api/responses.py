"""
responses.py - API 回應範例生成器
提供統一的 API 回應範例生成函數，減少重複代碼
"""

from typing import Dict, Any, Optional


def get_swagger_jwt_example() -> str:
    """
    取得 Swagger 文檔中的 JWT token 範例
    
    僅用於 Swagger 文檔中的回應範例，展示 JWT token 的格式
    實際 API 回應中的 JWT token 由 JWT 處理器動態生成
    
    Returns:
        Swagger 文檔用的 JWT token 範例字串
    """
    # 返回一個明顯的範例 token，避免與真實 token 混淆
    # 這個 token 僅用於 Swagger 文檔展示，不會用於實際驗證
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNjQwOTk1MjAwLCJleHAiOjE2NDA5OTg4MDAsInJvbGVzIjpbInVzZXIiXX0.SWAGGER_EXAMPLE_TOKEN_ONLY"


def success_response(
    data_example: Dict[str, Any], 
    description: str = "成功",
    status_code: int = 200
) -> Dict[int, Dict[str, Any]]:
    """
    生成成功回應範例
    
    Args:
        data_example: 成功回應的資料範例
        description: 回應描述
        status_code: HTTP 狀態碼，預設為 200
    
    Returns:
        包含成功回應範例的字典
    """
    return {
        status_code: {
            "description": description,
            "content": {
                "application/json": {
                    "example": {
                        "data": data_example,
                        "error": None
                    }
                }
            }
        }
    }


def error_response(
    status_code: int, 
    code: str, 
    message: str, 
    description: str = "錯誤"
) -> Dict[int, Dict[str, Any]]:
    """
    生成錯誤回應範例
    
    Args:
        status_code: HTTP 狀態碼
        code: 錯誤代碼
        message: 錯誤訊息
        description: 回應描述
    
    Returns:
        包含錯誤回應範例的字典
    """
    return {
        status_code: {
            "description": description,
            "content": {
                "application/json": {
                    "example": {
                        "data": None,
                        "error": {
                            "code": code,
                            "message": message
                        }
                    }
                }
            }
        }
    }


def combine_responses(*responses: Dict[int, Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    """
    合併多個回應範例
    
    Args:
        *responses: 多個回應範例字典
    
    Returns:
        合併後的回應範例字典
    """
    combined = {}
    for response in responses:
        combined.update(response)
    return combined
