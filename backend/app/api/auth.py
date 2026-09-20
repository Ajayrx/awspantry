"""Authentication endpoints — JWT Bearer.

Tokens are stateless; ``/logout`` is provided for the frontend contract
(client discards the token).
"""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.security import create_access_token, hash_password, verify_password
from app.dependencies import CurrentUser, DbDep
from app.models import User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.schemas.user import UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _issue_token(user: User) -> AuthResponse:
    return AuthResponse(
        access_token=create_access_token(str(user.id)),
        token_type="bearer",
        user=UserOut.model_validate(user),
    )


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an account",
    description="Registers a new user and immediately returns a JWT, so the "
    "frontend can treat signup as logged-in without a second round-trip.",
    responses={
        409: {"description": "Email already registered"},
        422: {"description": "Validation error"},
    },
)
def register(payload: RegisterRequest, db: DbDep) -> AuthResponse:
    email = payload.email.lower()
    existing = db.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )
    user = User(
        name=payload.name.strip(),
        email=email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _issue_token(user)


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Log in",
    description="Verifies credentials and returns "
    "`{access_token, token_type: 'bearer', user: {id, name, email}}`.",
    responses={
        401: {"description": "Invalid email or password"},
        422: {"description": "Validation error"},
    },
)
def login(payload: LoginRequest, db: DbDep) -> AuthResponse:
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return _issue_token(user)


@router.get(
    "/me",
    response_model=UserOut,
    summary="Current profile",
    description="Returns the user identified by the Bearer JWT.",
    responses={401: {"description": "Missing/invalid token"}},
)
def me(current_user: CurrentUser) -> UserOut:
    return UserOut.model_validate(current_user)


@router.post(
    "/logout",
    summary="Log out",
    description=(
        "SmartPantry uses stateless JWTs: the server does NOT revoke the "
        "token and does not maintain a blacklist (deliberate MVP choice). "
        "Logout = the CLIENT deletes its stored token; this endpoint "
        "simply confirms so the UI has a clean lifecycle hook. Until the "
        "token's natural expiry, anyone holding a leaked token could "
        "still use it — the README documents this limitation and the "
        "mitigation (rotate JWT_SECRET_KEY to invalidate every session)."
    ),
    responses={401: {"description": "Missing/invalid token"}},
)
def logout(current_user: CurrentUser) -> dict:
    return {
        "message": "Logged out — discard the stored token on this device.",
        "revokedOnServer": False,  # honest: stateless JWT, not revoked
    }
