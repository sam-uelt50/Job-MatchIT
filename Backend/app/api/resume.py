from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
import os
import shutil
from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from app.core.database import get_database
from app.core.config import settings
from app.services.resume_parser import ResumeParser
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
parser = ResumeParser()

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    is_primary: bool = Form(False),
    db=Depends(get_database)
):
    """
    Upload and parse a resume
    
    - **file**: PDF or DOCX file
    - **user_id**: ID of the user uploading the resume
    - **is_primary**: Whether this is the primary resume
    """
    
    # Validate file type
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    # Use the property correctly
    allowed_extensions = settings.ALLOWED_EXTENSIONS
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE // (1024 * 1024)}MB"
        )
    
    # Create upload directory
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().timestamp()
    safe_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"File saved: {file_path}")
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail="Error saving file")
    
    try:
        # Parse resume
        parsed_data = await parser.parse(file_path, file_ext[1:])
        
        # If this is first resume for user, set as primary
        existing_resumes = await db.resumes.count_documents({"user_id": user_id})
        if existing_resumes == 0:
            is_primary = True
        
        # If setting as primary, unset other primary resumes
        if is_primary:
            await db.resumes.update_many(
                {"user_id": user_id, "is_primary": True},
                {"$set": {"is_primary": False}}
            )
        
        # Save to database
        resume_doc = {
            "user_id": user_id,
            "file_name": file.filename,
            "file_path": file_path,
            "file_size": file_size,
            "is_primary": is_primary,
            "personal_info": parsed_data.get("personal_info", {}),
            "skills": parsed_data.get("skills", []),
            "experience": parsed_data.get("experience", []),
            "education": parsed_data.get("education", []),
            "certifications": parsed_data.get("certifications", []),
            "total_experience_years": parsed_data.get("total_experience_years", 0),
            "highest_education": parsed_data.get("highest_education", ""),
            "uploaded_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.resumes.insert_one(resume_doc)
        
        return {
            "message": "Resume uploaded and parsed successfully",
            "resume_id": str(result.inserted_id),
            "parsed_data": {
                "skills_count": len(parsed_data.get("skills", [])),
                "experience_years": parsed_data.get("total_experience_years", 0),
                "highest_education": parsed_data.get("highest_education", ""),
                "name": parsed_data.get("personal_info", {}).get("name", ""),
                "email": parsed_data.get("personal_info", {}).get("email", "")
            }
        }
        
    except Exception as e:
        # Clean up file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        logger.error(f"Error parsing resume: {e}")
        raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")

@router.get("/my-resumes")
async def get_my_resumes(
    user_id: str = Query(..., description="User ID"),
    db=Depends(get_database)
):
    """Get all resumes for a user"""
    
    resumes = await db.resumes.find({"user_id": user_id}).sort("uploaded_at", -1).to_list(length=50)
    
    result = []
    for resume in resumes:
        result.append({
            "id": str(resume["_id"]),
            "file_name": resume["file_name"],
            "file_size": resume["file_size"],
            "is_primary": resume.get("is_primary", False),
            "skills_count": len(resume.get("skills", [])),
            "experience_years": resume.get("total_experience_years", 0),
            "highest_education": resume.get("highest_education", ""),
            "uploaded_at": resume["uploaded_at"].isoformat() if resume.get("uploaded_at") else None
        })
    
    return {
        "total": len(result),
        "resumes": result
    }

@router.get("/{resume_id}")
async def get_resume(
    resume_id: str,
    include_parsed_data: bool = Query(False, description="Include full parsed data"),
    db=Depends(get_database)
):
    """Get a specific resume by ID"""
    
    try:
        resume = await db.resumes.find_one({"_id": ObjectId(resume_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid resume ID format")
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Build response
    response = {
        "id": str(resume["_id"]),
        "user_id": resume["user_id"],
        "file_name": resume["file_name"],
        "file_size": resume["file_size"],
        "is_primary": resume.get("is_primary", False),
        "uploaded_at": resume["uploaded_at"].isoformat() if resume.get("uploaded_at") else None
    }
    
    # Include parsed data if requested
    if include_parsed_data:
        response["personal_info"] = resume.get("personal_info", {})
        response["skills"] = resume.get("skills", [])
        response["experience"] = resume.get("experience", [])
        response["education"] = resume.get("education", [])
        response["certifications"] = resume.get("certifications", [])
        response["total_experience_years"] = resume.get("total_experience_years", 0)
        response["highest_education"] = resume.get("highest_education", "")
    
    return response

@router.put("/{resume_id}/set-primary")
async def set_primary_resume(
    resume_id: str,
    db=Depends(get_database)
):
    """Set a resume as primary for the user"""
    
    try:
        # Find the resume
        resume = await db.resumes.find_one({"_id": ObjectId(resume_id)})
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        user_id = resume["user_id"]
        
        # Unset current primary
        await db.resumes.update_many(
            {"user_id": user_id, "is_primary": True},
            {"$set": {"is_primary": False}}
        )
        
        # Set new primary
        await db.resumes.update_one(
            {"_id": ObjectId(resume_id)},
            {"$set": {"is_primary": True, "updated_at": datetime.utcnow()}}
        )
        
        return {"message": "Primary resume updated successfully"}
        
    except Exception as e:
        logger.error(f"Error setting primary resume: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    db=Depends(get_database)
):
    """Delete a resume"""
    
    try:
        resume = await db.resumes.find_one({"_id": ObjectId(resume_id)})
        
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Store file path before deletion
        file_path = resume.get("file_path")
        
        # Check if this was the primary resume
        was_primary = resume.get("is_primary", False)
        user_id = resume["user_id"]
        
        # Delete from database
        await db.resumes.delete_one({"_id": ObjectId(resume_id)})
        
        # Delete file if exists
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
            except Exception as e:
                logger.error(f"Error deleting file: {e}")
        
        # If deleted resume was primary, set another resume as primary
        if was_primary:
            next_resume = await db.resumes.find_one({"user_id": user_id})
            if next_resume:
                await db.resumes.update_one(
                    {"_id": next_resume["_id"]},
                    {"$set": {"is_primary": True}}
                )
        
        return {"message": "Resume deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting resume: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{resume_id}/parse")
async def reparse_resume(
    resume_id: str,
    db=Depends(get_database)
):
    """Reparse an existing resume (useful after updating parser)"""
    
    try:
        resume = await db.resumes.find_one({"_id": ObjectId(resume_id)})
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        file_path = resume["file_path"]
        file_ext = os.path.splitext(resume["file_name"])[1][1:]  # Remove dot
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Resume file not found")
        
        # Reparse the resume
        parsed_data = await parser.parse(file_path, file_ext)
        
        # Update database
        await db.resumes.update_one(
            {"_id": ObjectId(resume_id)},
            {
                "$set": {
                    "personal_info": parsed_data.get("personal_info", {}),
                    "skills": parsed_data.get("skills", []),
                    "experience": parsed_data.get("experience", []),
                    "education": parsed_data.get("education", []),
                    "certifications": parsed_data.get("certifications", []),
                    "total_experience_years": parsed_data.get("total_experience_years", 0),
                    "highest_education": parsed_data.get("highest_education", ""),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "message": "Resume reparsed successfully",
            "parsed_data": {
                "skills_count": len(parsed_data.get("skills", [])),
                "experience_years": parsed_data.get("total_experience_years", 0),
                "highest_education": parsed_data.get("highest_education", "")
            }
        }
        
    except Exception as e:
        logger.error(f"Error reparsing resume: {e}")
        raise HTTPException(status_code=500, detail=str(e))