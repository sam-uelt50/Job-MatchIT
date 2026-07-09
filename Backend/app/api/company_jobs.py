
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models import Company, Job, Application

router = APIRouter(prefix="/api/company", tags=["company"])

class JobCreate(BaseModel):
    title: str
    description: str
    requirements: str
    location: str = "Remote"
    salary_range: str = None
    employment_type: str = "full-time"
    is_remote: bool = True

@router.post("/jobs")
async def create_job(
    job: JobCreate,
    company_id: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    # Get company info
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    
    new_job = Job(
        id=str(uuid.uuid4()),
        company_id=company_id,
        company_name=company.company_name if company else "Unknown",
        title=job.title,
        description=job.description,
        requirements=job.requirements,
        location=job.location,
        salary_range=job.salary_range,
        employment_type=job.employment_type,
        is_remote=job.is_remote,
        created_at=datetime.utcnow()
    )
    db.add(new_job)
    await db.commit()
    
    return {"id": new_job.id, "title": new_job.title, "message": "Job created"}

@router.get("/jobs")
async def get_jobs(
    company_id: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Job).where(Job.company_id == company_id))
    jobs = result.scalars().all()
    
    return [
        {
            "id": job.id,
            "title": job.title,
            "location": job.location,
            "requirements": job.requirements,
            "salary_range": job.salary_range,
            "employment_type": job.employment_type,
            "is_remote": job.is_remote,
            "status": job.status,
            "created_at": job.created_at.isoformat() if job.created_at else None
        }
        for job in jobs
    ]

@router.get("/jobs/{job_id}/candidates")
async def get_candidates(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    # Get applications for this job
    result = await db.execute(
        select(Application).where(Application.job_id == job_id).order_by(Application.match_score.desc())
    )
    applications = result.scalars().all()
    
    return [
        {
            "candidate_id": app.user_id,
            "candidate_name": app.user_name,
            "email": app.user_email,
            "skills": app.user_skills.split(',') if app.user_skills else [],
            "experience_years": app.user_experience,
            "match_score": app.match_score,
            "rank_category": app.rank_category,
            "status": app.status,
            "applied_at": app.applied_at.isoformat() if app.applied_at else None
        }
        for app in applications
    ]

@router.post("/jobs/{job_id}/shortlist/{user_id}")
async def shortlist_candidate(
    job_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Application).where(
            and_(Application.job_id == job_id, Application.user_id == user_id)
        )
    )
    application = result.scalar_one_or_none()
    
    if application:
        application.status = "shortlisted"
        application.updated_at = datetime.utcnow()
        await db.commit()
        return {"message": "Candidate shortlisted successfully"}
    
    raise HTTPException(status_code=404, detail="Application not found")