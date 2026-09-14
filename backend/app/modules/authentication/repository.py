from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.authentication.models import User, StudentProfile


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def select(self, parameter: User):
        return select(parameter)

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def update(self, user: User) -> User:
        await self.session.flush()
        await self.session.refresh(user)
        return user


class StudentProfileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def select(self, parameter: StudentProfile):
        return select(parameter)

    async def get_by_id(self, profile_id: int) -> Optional[StudentProfile]:
        result = await self.session.execute(select(StudentProfile).where(StudentProfile.id == profile_id))
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> Optional[StudentProfile]:
        result = await self.session.execute(select(StudentProfile).where(StudentProfile.user_id == user_id))
        return result.scalar_one_or_none()

    async def get_by_student_id(self, student_id: str) -> Optional[StudentProfile]:
        result = await self.session.execute(select(StudentProfile).where(StudentProfile.student_id == student_id))
        return result.scalar_one_or_none()

    async def create(self, profile: StudentProfile) -> StudentProfile:
        self.session.add(profile)
        await self.session.flush()
        await self.session.refresh(profile)
        return profile

    async def update(self, profile: StudentProfile) -> StudentProfile:
        await self.session.flush()
        await self.session.refresh(profile)
        return profile