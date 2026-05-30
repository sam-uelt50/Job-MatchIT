from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.core.database import get_database
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/test")
async def test_recommendations():
    return {"message": "Recommendation engine is ready", "status": "online"}

@router.get("/jobs")
async def get_job_recommendations(
    user_id: str = Query(..., description="User ID"),
    limit: int = Query(10, ge=1, le=50),
    db=Depends(get_database)
):
    try:
        resume = await db.resumes.find_one({"user_id": user_id, "is_primary": True})
        if not resume:
            resume = await db.resumes.find_one({"user_id": user_id})
            if not resume:
                return {
                    "user_id": user_id,
                    "message": "No resume found. Please upload a resume first.",
                    "recommendations": []
                }
        
        jobs = await db.jobs.find({"status": "active"}).to_list(length=1000)
        user_skills = set([s.get("name", "").lower() for s in resume.get("skills", [])])
        recommendations = []
        
        for job in jobs:
            job_skills = set([s.lower() for s in job.get("required_skills", [])])
            
            if user_skills and job_skills:
                match_score = len(user_skills & job_skills) / len(job_skills) * 100
            else:
                match_score = 50
            
            category = "Strong Fit" if match_score >= 85 else "Moderate Fit" if match_score >= 60 else "Weak Fit"
            
            recommendations.append({
                "job_id": str(job["_id"]),
                "job_title": job.get("title", "Unknown"),
                "company": job.get("company", "Unknown"),
                "location": job.get("location", "Remote"),
                "match_score": round(match_score, 2),
                "category": category,
                "reason": f"Your skills match {len(user_skills & job_skills)} of {len(job_skills)} required skills" if job_skills else "No skills comparison available"
            })
        
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        
        return {
            "user_id": user_id,
            "total": len(recommendations),
            "recommendations": recommendations[:limit]
        }
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/candidates/{job_id}")
async def get_candidate_recommendations(
    job_id: str,
    min_score: float = Query(0, ge=0, le=100),
    limit: int = Query(20, ge=1, le=50),
    db=Depends(get_database)
):
    try:
        job = await db.jobs.find_one({"_id": ObjectId(job_id)})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        resumes = await db.resumes.find({}).to_list(length=1000)
        job_skills = set([s.lower() for s in job.get("required_skills", [])])
        recommendations = []
        
        for resume in resumes:
            resume_skills = set([s.get("name", "").lower() for s in resume.get("skills", [])])
            
            if job_skills and resume_skills:
                match_score = len(job_skills & resume_skills) / len(job_skills) * 100
            else:
                match_score = 50
            
            if match_score >= min_score:
                recommendations.append({
                    "candidate_id": resume["user_id"],
                    "resume_id": str(resume["_id"]),
                    "match_score": round(match_score, 2),
                    "skills": list(resume_skills)[:10]
                })
        
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        
        return {
            "job_id": job_id,
            "job_title": job["title"],
            "total": len(recommendations),
            "recommendations": recommendations[:limit]
        }
        
    except Exception as e:
        logger.error(f"Error getting candidate recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))