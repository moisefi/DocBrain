from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from docbrain.api.dependencies import get_app_settings, get_session
from docbrain.core.config import Settings
from docbrain.identity.passwords import PasswordService, WeakPasswordError
from docbrain.identity.tokens import JwtTokenService
from docbrain.identity.unit_of_work import SqlAlchemyIdentityUnitOfWork
from docbrain.identity.use_cases import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidOrganizationNameError,
    LoginCommand,
    LoginUseCase,
    RegisterUserCommand,
    RegisterUserUseCase,
)

router = APIRouter(prefix="/api/v1/auth")


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=256)
    organization_name: str = Field(min_length=1, max_length=200)
    display_name: str | None = Field(default=None, max_length=200)


class RegisterResponse(BaseModel):
    user_id: str
    organization_id: str
    role: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=256)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: str
    user_id: str


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    session: Annotated[Session, Depends(get_session)],
) -> RegisterResponse:
    def session_factory() -> Session:
        return session

    try:
        with SqlAlchemyIdentityUnitOfWork(session_factory) as uow:
            result = RegisterUserUseCase(
                users=uow.users,
                password_credentials=uow.password_credentials,
                organizations=uow.organizations,
                memberships=uow.memberships,
                password_service=PasswordService(),
            ).execute(
                RegisterUserCommand(
                    email=str(request.email),
                    password=request.password,
                    organization_name=request.organization_name,
                    display_name=request.display_name,
                ),
            )
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from exc
    except (InvalidOrganizationNameError, WeakPasswordError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return RegisterResponse(
        user_id=str(result.user.id.value),
        organization_id=str(result.organization.id.value),
        role=result.membership.role.value,
    )


@router.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest,
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> LoginResponse:
    def session_factory() -> Session:
        return session

    try:
        with SqlAlchemyIdentityUnitOfWork(session_factory) as uow:
            result = LoginUseCase(
                users=uow.users,
                password_credentials=uow.password_credentials,
                password_service=PasswordService(),
                token_service=JwtTokenService(settings),
            ).execute(
                LoginCommand(
                    email=str(request.email),
                    password=request.password,
                ),
            )
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        ) from exc

    return LoginResponse(
        access_token=result.access_token.value,
        expires_at=result.access_token.expires_at.isoformat(),
        user_id=str(result.user.id.value),
    )
