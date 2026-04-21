"""API response wrapper — canonical import path per project layout (`shared.api.wrapper`)."""

from shared.api.api_wrapper import (
    APIResponse,
    api_response,
    api_response_with_logging,
    handle_app_error,
    handle_domain_error,
    handle_system_error,
)

__all__ = [
    "APIResponse",
    "api_response",
    "api_response_with_logging",
    "handle_domain_error",
    "handle_app_error",
    "handle_system_error",
]
