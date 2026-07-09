from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class EmploymentType(str, Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    REMOTE = "remote"

class JobBase(BaseModel):
    title: str
    company: str
    description: str
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    location: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    experience_level: Optional[str] = None

class JobCreate(JobBase):
    recruiter_id: str

class JobResponse(JobBase):
    id: str
    recruiter_id: str
    status: str = "active"
    applicant_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True