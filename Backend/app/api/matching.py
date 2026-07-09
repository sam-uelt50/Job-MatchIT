from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.core.database import get_database
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/test")
async def test_matching():
    return {"message": "Matching engine is ready", "status": "online"}

@router.get("/job/{job_id}/candidates")
async def match_candidates_for_job(
    job_id: str,
    min_score: float = Query(0, ge=0, le=100),
    limit: int = Query(20, ge=1, le=100),
    db=Depends(get_database)
):
    try:
        job = await db.jobs.find_one({"_id": ObjectId(job_id)})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        resumes = await db.resumes.find({}).to_list(length=1000)
        matches = []
        
        for resume in resumes:
            job_skills = set(job.get("required_skills", []))
            resume_skills = set([s.get("name", "").lower() for s in resume.get("skills", [])])
            
            if job_skills and resume_skills:
                match_score = len(job_skills & resume_skills) / len(job_skills) * 100
            else:
                match_score = 50
            
            if match_score >= min_score:
                category = "Strong Fit" if match_score >= 85 else "Moderate Fit" if match_score >= 60 else "Weak Fit"
                matches.append({
                    "resume_id": str(resume["_id"]),
                    "candidate_id": resume["user_id"],
                    "match_score": round(match_score, 2),
                    "category": category
                })
        
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return {
            "job_id": job_id,
            "job_title": job["title"],
            "total_matches": len(matches),
            "matches": matches[:limit]
        }
        
    except Exception as e:
        logger.error(f"Error matching candidates: {e}")
        raise HTTPException(status_code=500, detail=str(e))