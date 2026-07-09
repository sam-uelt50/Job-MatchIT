from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class ApplicationStatus(str, Enum):
    APPLIED = "applied"
    REVIEWED = "reviewed"
    SHORTLISTED = "shortlisted"
    INTERVIEW = "interview"
    OFFERED = "offered"
    HIRED = "hired"
    REJECTED = "rejected"

class MatchCategory(str, Enum):
    STRONG_FIT = "Strong Fit"
    MODERATE_FIT = "Moderate Fit"
    WEAK_FIT = "Weak Fit"

class ApplicationBase(BaseModel):
    job_id: str
    resume_id: str

class ApplicationCreate(ApplicationBase):
    candidate_id: str

class ApplicationResponse(ApplicationBase):
    id: str
    candidate_id: str
    match_score: float
    skill_score: Optional[float] = None
    experience_score: Optional[float] = None
    education_score: Optional[float] = None
    semantic_score: Optional[float] = None
    rank_category: MatchCategory
    strengths: List[str] = []
    gaps: List[str] = []
    status: ApplicationStatus = ApplicationStatus.APPLIED
    created_at: datetime
    
    class Config:
        from_attributes = True