from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId
from app.core.database import get_database
from datetime import datetime

router = APIRouter()

@router.post("/apply")
async def apply_to_job(
    job_id: str,
    candidate_id: str,
    resume_id: str,
    db=Depends(get_database)
):
    existing = await db.applications.find_one({
        "candidate_id": candidate_id,
        "job_id": job_id
    })
    if existing:
        raise HTTPException(status_code=400, detail="Already applied")
    
    application = {
        "candidate_id": candidate_id,
        "job_id": job_id,
        "resume_id": resume_id,
        "match_score": 0,
        "rank_category": "Pending",
        "status": "applied",
        "created_at": datetime.utcnow()
    }
    
    result = await db.applications.insert_one(application)
    
    return {
        "message": "Application submitted",
        "application_id": str(result.inserted_id)
    }
