from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from bson import ObjectId

class SkillMatchDetail(BaseModel):
    skill: str
    required: bool
    matched: bool
    candidate_proficiency: Optional[str] = None
    required_proficiency: Optional[str] = None
    importance: str = "required"
    contribution: float = 0.0

class ExperienceMatchDetail(BaseModel):
    required_years: float
    candidate_years: float
    years_score: float
    level_match: bool
    level_score: float
    relevant_roles: List[str] = []
    missing_experience: List[str] = []

class EducationMatchDetail(BaseModel):
    required_level: str
    candidate_level: str
    level_match: bool
    field_match: bool
    level_score: float
    field_score: float
    overall_score: float

class SemanticMatchDetail(BaseModel):
    similarity_score: float
    key_matching_phrases: List[Dict[str, float]] = []
    key_missing_concepts: List[str] = []

class MatchResult(BaseModel):
    """
    MongoDB document for storing detailed match results
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    
    # References
    resume_id: str
    job_id: str
    application_id: Optional[str] = None
    
    # Overall scores
    total_score: float
    fit_category: str  # Strong Fit, Moderate Fit, Weak Fit
    
    # Component scores
    skill_match_score: float
    experience_match_score: float
    education_match_score: float
    semantic_match_score: float
    
    # Detailed breakdowns
    skill_details: List[SkillMatchDetail] = []
    experience_details: ExperienceMatchDetail
    education_details: EducationMatchDetail
    semantic_details: SemanticMatchDetail
    
    # Summaries
    matched_skills: List[str] = []
    missing_required_skills: List[str] = []
    missing_preferred_skills: List[str] = []
    additional_skills: List[str] = []
    
    # Strengths and gaps
    strengths: List[str] = []
    gaps: List[str] = []
    recommendations: List[str] = []  # How to improve
    
    # Explainability
    top_contributing_factors: List[Dict[str, Any]] = []
    explanation_text: str
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    match_version: str = "1.0"
    processing_time_ms: int = 0
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class BatchMatchSummary(BaseModel):
    job_id: str
    total_candidates: int
    average_score: float
    distribution: Dict[str, int]  # Strong, Moderate, Weak counts
    top_candidates: List[Dict[str, Any]]
    created_at: datetime = Field(default_factory=datetime.utcnow)