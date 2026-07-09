# app/api/jobs_sqlite.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.core.sqlite_database import get_db
from app.models import Job, User

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

# Pydantic models for request/response
class JobCreate(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    salary_range: Optional[str] = None
    employment_type: str = "full-time"

class JobResponse(BaseModel):
    id: str
    title: str
    company: str
    location: Optional[str]
    description: Optional[str]
    requirements: Optional[str]
    salary_range: Optional[str]
    employment_type: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    salary_range: Optional[str] = None
    employment_type: Optional[str] = None
    status: Optional[str] = None

@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    db: AsyncSession = Depends(get_db),
    # user_id: str = Depends(get_current_user)  # Add auth later
):
    """Create a new job posting"""
    # For now, use a temporary user ID (replace with actual auth)
    temp_user_id = "temp_user_001"
    
    new_job = Job(
        id=str(uuid.uuid4()),
        title=job_data.title,
        company=job_data.company,
        location=job_data.location,
        description=job_data.description,
        requirements=job_data.requirements,
        salary_range=job_data.salary_range,
        employment_type=job_data.employment_type,
        user_id=temp_user_id
    )
    
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    
    return new_job

@router.get("/", response_model=List[JobResponse])
async def get_jobs(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = "active",
    db: AsyncSession = Depends(get_db)
):
    """Get all jobs with pagination"""
    query = select(Job)
    
    if status_filter:
        query = query.where(Job.status == status_filter)
    
    query = query.offset(skip).limit(limit).order_by(Job.created_at.desc())
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return jobs

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific job by ID"""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job

@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: str,
    job_update: JobUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a job"""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Update only provided fields
    update_data = job_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)
    
    await db.commit()
    await db.refresh(job)
    
    return job

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a job"""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    await db.delete(job)
    await db.commit()
    
    return None

@router.get("/stats/count")
async def get_job_stats(db: AsyncSession = Depends(get_db)):
    """Get job statistics"""
    total_result = await db.execute(select(func.count()).select_from(Job))
    active_result = await db.execute(select(func.count()).where(Job.status == "active"))
    
    return {
        "total_jobs": total_result.scalar(),
        "active_jobs": active_result.scalar()
    }