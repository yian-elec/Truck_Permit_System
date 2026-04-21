"""IAM application errors."""

from .iam_app_errors import (
    IamAccountNotAllowedError,
    IamAssignRoleForbiddenError,
    IamEmailAlreadyRegisteredError,
    IamExternalLoginNotSupportedError,
    IamInputValidationError,
    IamInvalidCredentialsError,
    IamMfaChallengeInvalidError,
    IamMobileAlreadyRegisteredError,
    IamRefreshTokenInvalidError,
    IamRoleNotFoundError,
    IamSessionNotFoundError,
    IamUserNotFoundError,
)

__all__ = [
    "IamAccountNotAllowedError",
    "IamAssignRoleForbiddenError",
    "IamEmailAlreadyRegisteredError",
    "IamExternalLoginNotSupportedError",
    "IamInputValidationError",
    "IamInvalidCredentialsError",
    "IamMfaChallengeInvalidError",
    "IamMobileAlreadyRegisteredError",
    "IamRefreshTokenInvalidError",
    "IamRoleNotFoundError",
    "IamSessionNotFoundError",
    "IamUserNotFoundError",
]
