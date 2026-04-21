"""IAM application DTOs."""

from .assign_role_dto import AssignRoleInputDTO, AssignRoleOutputDTO, AssignRoleRequestBodyDTO
from .auth_logout_dto import IamLogoutInputDTO, IamLogoutOutputDTO, IamLogoutRequestBodyDTO
from .auth_me_dto import IamMeOutputDTO
from .auth_permissions_dto import IamPermissionsOutputDTO
from .auth_refresh_dto import IamRefreshInputDTO, IamRefreshOutputDTO
from .login_iam_dto import LoginIamInputDTO, LoginIamOutputDTO
from .mfa_verify_dto import MfaVerifyInputDTO, MfaVerifyOutputDTO
from .register_applicant_dto import RegisterApplicantInputDTO, RegisterApplicantOutputDTO

__all__ = [
    "AssignRoleInputDTO",
    "AssignRoleOutputDTO",
    "AssignRoleRequestBodyDTO",
    "IamLogoutInputDTO",
    "IamLogoutOutputDTO",
    "IamLogoutRequestBodyDTO",
    "IamMeOutputDTO",
    "IamPermissionsOutputDTO",
    "IamRefreshInputDTO",
    "IamRefreshOutputDTO",
    "LoginIamInputDTO",
    "LoginIamOutputDTO",
    "MfaVerifyInputDTO",
    "MfaVerifyOutputDTO",
    "RegisterApplicantInputDTO",
    "RegisterApplicantOutputDTO",
]
