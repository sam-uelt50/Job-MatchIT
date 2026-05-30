from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from app.core.database import get_database
from app.models.job import JobCreate, JobResponse
from bson import ObjectId
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=dict)
async def create_job(job: JobCreate, db=Depends(get_database)):
    """Create a new job posting"""
    
    job_dict = job.dict()
    job_dict["status"] = "active"
    job_dict["applicant_count"] = 0
    job_dict["created_at"] = datetime.utcnow()
    job_dict["updated_at"] = datetime.utcnow()
    
    result = await db.jobs.insert_one(job_dict)
    
    return {
        "message": "Job created successfully",
        "job_id": str(result.inserted_id)
    }

@router.get("/", response_model=dict)
async def get_jobs(
    status: Optional[str] = Query("active"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db=Depends(get_database)
):
    """Get all jobs with pagination"""
    
    query = {"status": status} if status else {}
    
    total = await db.jobs.count_documents(query)
    jobs = await db.jobs.find(query).skip(skip).limit(limit).to_list(length=limit)
    
    for job in jobs:
        job["id"] = str(job["_id"])
        del job["_id"]
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "jobs": jobs
    }

@router.get("/{job_id}", response_model=dict)
async def get_job(job_id: str, db=Depends(get_database)):
    """Get a specific job by ID"""
    
    try:
        job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid job ID")
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job["id"] = str(job["_id"])
    del job["_id"]
    
    return job

@router.put("/{job_id}/status")
async def update_job_status(
    job_id: str,
    status: str,
    db=Depends(get_database)
):
    """Update job status (active, closed)"""
    
    try:
        result = await db.jobs.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}}
        )
    except:
        raise HTTPException(status_code=400, detail="Invalid job ID")
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"message": f"Job status updated to {status}"}

@router.delete("/{job_id}")
async def delete_job(job_id: str, db=Depends(get_database)):
    """Delete a job posting"""
    
    try:
        result = await db.jobs.delete_one({"_id": ObjectId(job_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid job ID")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"message": "Job deleted successfully"}