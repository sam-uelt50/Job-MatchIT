from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class PersonalInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None

class Skill(BaseModel):
    name: str
    confidence: float = 1.0

class Experience(BaseModel):
    company: str
    title: str
    start_date: str
    end_date: Optional[str] = None
    is_current: bool = False
    description: str

class Education(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class ResumeBase(BaseModel):
    file_name: str
    is_primary: bool = False

class ResumeCreate(ResumeBase):
    user_id: str

class ResumeResponse(ResumeBase):
    id: str
    user_id: str
    file_path: str
    file_size: int
    personal_info: PersonalInfo = PersonalInfo()
    skills: List[Skill] = []
    experience: List[Experience] = []
    education: List[Education] = []
    total_experience_years: float = 0
    uploaded_at: datetime
    
    class Config:
        from_attributes = True