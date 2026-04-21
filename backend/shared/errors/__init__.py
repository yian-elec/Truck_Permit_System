"""
shared/errors - 統一錯誤處理系統
提供所有錯誤類別的統一匯出
"""

# Base Error
from .base_error import BaseError

# Domain Errors
from .domain_error import DomainError, ValidationError, NotFoundError

# App Errors
from .app_error import AppError, ForbiddenError, ConflictError

# System Errors
from .system_error import (
    SystemError, 
    AuthError, 
    InternalError, 
    TimeoutError,
    MissingTokenError,
    InvalidTokenError,
    ExpiredTokenError,
    DBConnectionException,
    ConfigurationException,
    ServiceUnavailableException,
    ExternalAPITimeoutException,
    DatabaseTimeoutException
)

__all__ = [
    # Base
    "BaseError",
    
    # Domain
    "DomainError",
    "ValidationError", 
    "NotFoundError",
    
    # App
    "AppError",
    "ForbiddenError",
    "ConflictError",
    
    # System
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
