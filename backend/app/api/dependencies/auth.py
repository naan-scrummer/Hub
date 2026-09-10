from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.base import get_db
from app.modules.authentication.models import User
from app.modules.authentication.repository import UserRepository
from app.modules.authentication.service import AuthenticationService
from app.logging.config import get_logger


settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
logger = get_logger(__name__)


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthenticationService:
    user_repo = UserRepository(db)
    from app.modules.authentication.repository import StudentProfileRepository
    profile_repo = StudentProfileRepository(db)
    return AuthenticationService(user_repo, profile_repo)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthenticationService = Depends(get_auth_service),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = auth_service.decode_token(token)
    if not payload or payload.get("type") != "access":
        raise credentials_exception
    user_id: str = payload.get("sub")
    if not user_id:
        raise credentials_exception
    user = await auth_service.get_current_user(token)
    if user is None:
        raise credentials_exception
    return user


async def get_current_student_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.authentication.repository import StudentProfileRepository
    profile_repo = StudentProfileRepository(db)
    profile = await profile_repo.get_by_user_id(current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )
    return profile