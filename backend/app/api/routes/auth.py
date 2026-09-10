from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.modules.authentication.service import AuthenticationService
from app.modules.authentication.repository import UserRepository, StudentProfileRepository
from app.api.dependencies.auth import get_current_user, get_current_student_profile
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    StudentProfileResponse,
)
from app.modules.authentication.models import User
from app.logging.config import get_logger


router = APIRouter(prefix="/auth", tags=["authentication"])
logger = get_logger(__name__)


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthenticationService:
    user_repo = UserRepository(db)
    profile_repo = StudentProfileRepository(db)
    return AuthenticationService(user_repo, profile_repo)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    user = await auth_service.authenticate(request.email, request.password)
    if not user:
        logger.warning("login_failed", email=request.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_service.create_access_token({"sub": str(user.id), "email": user.email, "role": user.role.value})
    refresh_token = auth_service.create_refresh_token({"sub": str(user.id), "email": user.email})

    logger.info("login_success", user_id=user.id, email=user.email)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    access_token = await auth_service.refresh_access_token(request.refresh_token)
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    return TokenResponse(access_token=access_token, refresh_token=request.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.value,
        is_active=current_user.is_active,
    )


@router.get("/profile", response_model=StudentProfileResponse)
async def get_student_profile(profile = Depends(get_current_student_profile)):
    return StudentProfileResponse(
        id=profile.id,
        student_id=profile.student_id,
        department=profile.department,
        semester=profile.semester,
        section=profile.section,
    )


@router.post("/logout")
async def logout():
    # Client-side token removal; server-side token blacklist could be added
    return {"message": "Successfully logged out"}