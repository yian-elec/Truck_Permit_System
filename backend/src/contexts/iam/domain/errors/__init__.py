"""IAM domain errors."""

from .iam_errors import (
    IamDomainError,
    InvalidAssignmentScopePairError,
    InvalidCredentialInvariantError,
    InvalidDisplayNameError,
    InvalidIamCodeFormatError,
    InvalidIamIdError,
    InvalidUserStateError,
    MfaChallengeAlreadyVerifiedError,
    MfaChallengeExpiredError,
    MfaChallengeInvariantViolationError,
    OfficerAdminRequiresMfaError,
    OfficerAdminRequiresRoleError,
    SessionInvariantViolationError,
    SessionNotActiveError,
)

__all__ = [
    "IamDomainError",
    "InvalidAssignmentScopePairError",
    "InvalidCredentialInvariantError",
    "InvalidDisplayNameError",
    "InvalidIamCodeFormatError",
    "InvalidIamIdError",
    "InvalidUserStateError",
    "MfaChallengeAlreadyVerifiedError",
    "MfaChallengeExpiredError",
    "MfaChallengeInvariantViolationError",
    "OfficerAdminRequiresMfaError",
    "OfficerAdminRequiresRoleError",
    "SessionInvariantViolationError",
    "SessionNotActiveError",
]
