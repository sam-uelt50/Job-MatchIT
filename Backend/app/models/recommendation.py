from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from bson import ObjectId

class RecommendationFactor(BaseModel):
    factor: str
    weight: float
    contribution: float
    description: str

class JobRecommendation(BaseModel):
    """
    MongoDB document for job recommendations (for candidates)
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    
    # References
    user_id: str
    resume_id: str
    job_id: str
    
    # Recommendation details
    score: float
    fit_category: str
    recommendation_type: str  # content-based, collaborative, hybrid
    
    # Why recommended
    matching_factors: List[RecommendationFactor] = []
    strengths: List[str] = []
    potential_gaps: List[str] = []
    explanation: str
    
    # User interaction
    is_viewed: bool = False
    is_saved: bool = False
    is_applied: bool = False
    viewed_at: Optional[datetime] = None
    saved_at: Optional[datetime] = None
    applied_at: Optional[datetime] = None
    
    # User feedback
    feedback_rating: Optional[int] = None  # 1-5
    feedback_text: Optional[str] = None
    feedback_categories: List[str] = []
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    version: str = "1.0"
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CandidateRecommendation(BaseModel):
    """
    MongoDB document for candidate recommendations (for recruiters)
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    
    # References
    job_id: str
    recruiter_id: str
    candidate_id: str
    resume_id: str
    
    # Recommendation details
    match_score: float
    fit_category: str
    
    # Candidate snapshot (denormalized for performance)
    candidate_name: str
    candidate_location: Optional[str] = None
    total_experience_years: float
    top_skills: List[str] = []
    current_title: Optional[str] = None
    current_company: Optional[str] = None
    highest_education: Optional[str] = None
    
    # Match details
    skill_match_percentage: float
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    strengths: List[str] = []
    gaps: List[str] = []
    
    # Recruiter interaction
    is_viewed: bool = False
    is_contacted: bool = False
    viewed_at: Optional[datetime] = None
    contacted_at: Optional[datetime] = None
    notes: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    rank: int = 0
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}