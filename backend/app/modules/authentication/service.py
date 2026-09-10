from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import get_settings
from app.modules.authentication.models import User, UserRole, StudentProfile
from app.modules.authentication.repository import UserRepository, StudentProfileRepository
from app.logging.config import get_logger


settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = get_logger(__name__)


class AuthenticationService:
    def __init__(
        self,
        user_repo: UserRepository,
        profile_repo: StudentProfileRepository,
    ):
        self.user_repo = user_repo
        self.profile_repo = profile_repo

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def create_refresh_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def decode_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        user = await self.user_repo.get_by_email(email)
        if not user or not user.is_active:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    async def get_current_user(self, token: str) -> Optional[User]:
        payload = self.decode_token(token)
        if not payload or payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
        return await self.user_repo.get_by_id(int(user_id))

    async def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        payload = self.decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
        user = await self.user_repo.get_by_id(int(user_id))
        if not user or not user.is_active:
            return None
        return self.create_access_token({"sub": str(user.id), "email": user.email, "role": user.role.value})

    async def create_demo_user(self) -> User:
        existing = await self.user_repo.get_by_email(settings.DEMO_STUDENT_EMAIL)
        if existing:
            return existing

        hashed_password = self.get_password_hash(settings.DEMO_STUDENT_PASSWORD)
        user = User(
            email=settings.DEMO_STUDENT_EMAIL,
            hashed_password=hashed_password,
            full_name="Demo Student",
            role=UserRole.STUDENT,
        )
        user = await self.user_repo.create(user)

        profile = StudentProfile(
            user_id=user.id,
            student_id="STU2024001",
            department="Computer Science",
            semester=6,
            section="A",
        )
        await self.profile_repo.create(profile)

        logger.info("demo_user_created", user_id=user.id, email=user.email)
        return user