"""
SystemError - System 層錯誤
用於系統與技術性錯誤 (安全、基礎設施、外部 API)
狀態碼：401 Unauthorized, 500 Internal Server Error, 504 Gateway Timeout
"""

from .system_error import SystemError
from .auth_error import AuthError, MissingTokenError, InvalidTokenError, ExpiredTokenError
from .internal_error import InternalError, DBConnectionException, ConfigurationException, ServiceUnavailableException
from .timeout_error import TimeoutError, ExternalAPITimeoutException, DatabaseTimeoutException

__all__ = [
    "SystemError", 
    "AuthError", 
    "InternalError", 
    "TimeoutError",
    "MissingTokenError",
    "InvalidTokenError", 
    "ExpiredTokenError",
    "DBConnectionException",
    "ConfigurationException",
    "ServiceUnavailableException",
    "ExternalAPITimeoutException",
    "DatabaseTimeoutException"
]
