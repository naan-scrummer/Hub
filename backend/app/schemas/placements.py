from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class CompanyResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    website: Optional[str]
    industry: Optional[str]

    class Config:
        from_attributes = True


class PlacementOpportunityResponse(BaseModel):
    id: int
    company_id: int
    company_name: Optional[str] = None
    title: str
    description: Optional[str]
    eligibility_criteria: Optional[str]
    location: Optional[str]
    package_details: Optional[str]
    application_deadline: Optional[datetime]
    recruitment_status: str
    created_at: datetime

    class Config:
        from_attributes = True


class PlacementContributionResponse(BaseModel):
    id: int
    student_id: int
    company_id: int
    company_name: Optional[str] = None
    title: str
    content: str
    contribution_type: str
    is_published: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PlacementOpportunityListResponse(BaseModel):
    opportunities: List[PlacementOpportunityResponse]


class PlacementContributionListResponse(BaseModel):
    contributions: List[PlacementContributionResponse]


class PlacementContributionCreateRequest(BaseModel):
    company_id: int
    title: str
    content: str
    contribution_type: str

class PlacementSyncRequest(BaseModel):
    pass