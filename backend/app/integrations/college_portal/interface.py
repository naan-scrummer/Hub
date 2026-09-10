from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from app.modules.attendance.models import AttendanceRecord
from app.modules.academics.models import AcademicRecord
from app.modules.examinations.models import Examination
from app.modules.announcements.models import Announcement, AnnouncementSource
from app.modules.placements.models import Company, PlacementOpportunity


class CollegePortalClient(ABC):
    @abstractmethod
    async def fetch_attendance(self, student_id: str) -> List[dict]:
        pass

    @abstractmethod
    async def fetch_academics(self, student_id: str) -> List[dict]:
        pass

    @abstractmethod
    async def fetch_examinations(self) -> List[dict]:
        pass

    @abstractmethod
    async def fetch_announcements(self, source: AnnouncementSource) -> List[dict]:
        pass

    @abstractmethod
    async def fetch_placements(self) -> List[dict]:
        pass


class AttendancePortalAdapter(ABC):
    @abstractmethod
    async def sync(self, student_id: int, sync_run_id: int) -> List[AttendanceRecord]:
        pass


class AcademicPortalAdapter(ABC):
    @abstractmethod
    async def sync(self, student_id: int, sync_run_id: int) -> List[AcademicRecord]:
        pass


class ExaminationPortalAdapter(ABC):
    @abstractmethod
    async def sync(self, sync_run_id: int) -> List[Examination]:
        pass


class AnnouncementPortalAdapter(ABC):
    @abstractmethod
    async def sync(self, source: AnnouncementSource, sync_run_id: int) -> List[Announcement]:
        pass


class PlacementPortalAdapter(ABC):
    @abstractmethod
    async def sync(self, sync_run_id: int) -> List[PlacementOpportunity]:
        pass