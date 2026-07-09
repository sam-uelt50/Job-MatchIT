# app/api/resume_screening.py
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from typing import List, Optional
import json
import uuid

from app.core.resume_parser import ResumeParser
from app.core.job_matcher import JobMatcher

router = APIRouter(prefix="/api/screening", tags=["resume-screening"])

# Initialize components
resume_parser = ResumeParser()
job_matcher = JobMatcher()

@router.post("/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    """Parse and analyze a single resume"""
    try:
        parsed_data = resume_parser.parse_resume(file)
        return {
            "status": "success",
            "filename": file.filename,
            "analysis": {
                "skills_found": parsed_data.get('skills', []),
                "experience_years": parsed_data.get('experience_years', 0),
                "education": parsed_data.get('education', {}),
                "email": parsed_data.get('email'),
                "phone": parsed_data.get('phone'),
                "word_count": parsed_data.get('word_count', 0)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/match-candidate-to-job")
async def match_candidate_to_job(
    resume_file: UploadFile = File(...),
    job_id: str = Form(...)
):
    """Match a candidate resume against a specific job"""
    try:
        # Parse resume
        resume_data = resume_parser.parse_resume(resume_file)
        
        # In a real implementation, fetch job from database
        # For now, create a mock job based on the ID
        job_data = {
            "id": job_id,
            "required_skills": ["python", "fastapi", "sql", "docker", "aws"],
            "required_experience": 3,
            "description": "Looking for a Python developer with FastAPI experience"
        }
        
        # Calculate match
        match_result = job_matcher.rank_candidates(resume_data, job_data)
        
        return {
            "status": "success",
            "match_result": match_result,
            "candidate_skills": resume_data.get('skills', []),
            "experience": resume_data.get('experience_years', 0)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/batch-rank-candidates")
async def batch_rank_candidates(
    resume_files: List[UploadFile] = File(...),
    job_id: str = Form(...)
):
    """Rank multiple candidates for a single job"""
    try:
        # Parse all resumes
        candidates = []
        for resume in resume_files:
            parsed = resume_parser.parse_resume(resume)
            candidates.append({
                "id": str(uuid.uuid4()),
                "name": resume.filename,
                **parsed
            })
        
        # Mock job data
        job_data = {
            "id": job_id,
            "required_skills": ["python", "fastapi", "sql", "docker", "aws"],
            "required_experience": 3,
            "description": "Looking for a Python developer with FastAPI experience"
        }
        
        # Rank candidates
        ranked = job_matcher.rank_multiple_candidates(candidates, job_data)
        
        return {
            "status": "success",
            "total_candidates": len(candidates),
            "ranked_candidates": ranked
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/recommend-jobs-for-candidate")
async def recommend_jobs(
    resume_file: UploadFile = File(...),
    limit: int = Form(5)
):
    """Recommend jobs based on resume"""
    try:
        # Parse resume
        resume_data = resume_parser.parse_resume(resume_file)
        
        # Mock jobs list (in real implementation, fetch from database)
        jobs = [
            {
                "id": "1",
                "title": "Python Developer",
                "company": "Tech Corp",
                "required_skills": ["python", "fastapi", "sql"],
                "required_experience": 2,
                "description": "Python development"
            },
            {
                "id": "2",
                "title": "Data Scientist",
                "company": "AI Solutions",
                "required_skills": ["python", "pandas", "scikit-learn"],
                "required_experience": 2,
                "description": "Data science work"
            }
        ]
        
        # Get recommendations
        recommendations = job_matcher.recommend_jobs(resume_data, jobs, limit)
        
        return {
            "status": "success",
            "candidate_skills": resume_data.get('skills', []),
            "experience_years": resume_data.get('experience_years', 0),
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))