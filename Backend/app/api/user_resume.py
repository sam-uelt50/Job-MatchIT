
from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Depends
from typing import List, Optional
import uuid
import re
from datetime import datetime
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models import User, Company, Job, Application

router = APIRouter(prefix="/api/user", tags=["user"])

# Skill database
SKILLS = ['python', 'java', 'javascript', 'react', 'angular', 'vue', 'django', 'flask', 'fastapi', 
          'sql', 'mongodb', 'postgresql', 'docker', 'kubernetes', 'aws', 'azure', 'git', 'tensorflow', 
          'pytorch', 'pandas', 'numpy', 'html', 'css', 'figma', 'ui/ux']

def extract_skills(text: str) -> List[str]:
    text_lower = text.lower()
    return [s.title() for s in SKILLS if s in text_lower][:10]

def extract_experience(text: str) -> int:
    matches = re.findall(r'(\d+)\+?\s*years?', text.lower())
    for match in matches:
        years = int(match)
        if 1 <= years <= 20:
            return years
    return 2

@router.post("/upload-resume")
async def upload_resume(
    resume_file: UploadFile = File(...),
    user_id: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        content = await resume_file.read()
        text = content.decode('utf-8', errors='ignore')
        
        skills = extract_skills(text)
        experience = extract_experience(text)
        
        # Update user profile
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.skills = ','.join(skills)
            user.experience_years = experience
            user.resume_text = text[:5000]
            await db.commit()
        
        return {
            "message": "Resume parsed successfully",
            "skills": skills,
            "experience_years": experience,
            "word_count": len(text.split())
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/recommendations")
async def get_recommendations(
    user_id: str = Query(...),
    limit: int = Query(5),
    db: AsyncSession = Depends(get_db)
):
    # Get user skills
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    user_skills = user.skills.split(',') if user and user.skills else []
    user_experience = user.experience_years if user else 0
    
    # Get all active jobs
    result = await db.execute(select(Job).where(Job.status == "active"))
    jobs = result.scalars().all()
    
    recommendations = []
    for job in jobs:
        # Calculate match score
        job_skills = [s.strip().lower() for s in job.requirements.split(',')] if job.requirements else []
        user_skills_lower = [s.lower() for s in user_skills]
        
        matched = sum(1 for s in job_skills if s in user_skills_lower)
        skill_match = (matched / len(job_skills) * 100) if job_skills else 0
        
        exp_match = 100 if user_experience >= 3 else (user_experience / 3 * 100)
        total_match = (skill_match * 0.7) + (exp_match * 0.3)
        
        rank = "Top Match" if total_match >= 80 else "Good Match" if total_match >= 60 else "Potential Match"
        
        recommendations.append({
            "job_id": job.id,
            "job_title": job.title,
            "company": job.company_name,
            "location": job.location,
            "match_score": round(total_match, 1),
            "rank_category": rank,
            "breakdown": {"skills": round(skill_match, 1), "experience": round(exp_match, 1)}
        })
    
    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    
    return {
        "user": {"skills": user_skills, "experience_years": user_experience},
        "recommendations": recommendations[:limit]
    }

@router.post("/apply/{job_id}")
async def apply_for_job(
    job_id: str,
    user_id: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Get user info
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get job info
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Check if already applied
        result = await db.execute(
            select(Application).where(
                and_(Application.user_id == user_id, Application.job_id == job_id)
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail="Already applied for this job")
        
        # Calculate match score
        user_skills = user.skills.split(',') if user.skills else []
        job_skills = [s.strip().lower() for s in job.requirements.split(',')] if job.requirements else []
        user_skills_lower = [s.lower() for s in user_skills]
        
        matched = sum(1 for s in job_skills if s in user_skills_lower)
        skill_match = (matched / len(job_skills) * 100) if job_skills else 0
        exp_match = 100 if user.experience_years >= 3 else (user.experience_years / 3 * 100)
        total_match = (skill_match * 0.7) + (exp_match * 0.3)
        rank = "Top Match" if total_match >= 80 else "Good Match" if total_match >= 60 else "Potential Match"
        
        # Create application
        application = Application(
            id=str(uuid.uuid4()),
            user_id=user_id,
            user_name=user.full_name,
            user_email=user.email,
            user_skills=user.skills,
            user_experience=user.experience_years,
            job_id=job_id,
            job_title=job.title,
            company_id=job.company_id,
            company_name=job.company_name,
            match_score=round(total_match, 1),
            rank_category=rank,
            status="applied",
            applied_at=datetime.utcnow()
        )
        
        db.add(application)
        await db.commit()
        
        return {
            "message": "Application submitted successfully!",
            "application_id": application.id,
            "match_score": application.match_score,
            "rank_category": application.rank_category
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/applications")
async def get_applications(
    user_id: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Get user's applications"""
    result = await db.execute(
        select(Application).where(Application.user_id == user_id).order_by(Application.applied_at.desc())
    )
    applications = result.scalars().all()
    
    return [
        {
            "application_id": app.id,
            "job_title": app.job_title,
            "company_name": app.company_name,
            "match_score": app.match_score,
            "rank_category": app.rank_category,
            "status": app.status,
            "applied_at": app.applied_at.isoformat() if app.applied_at else None
        }
        for app in applications
    ]