# app/api/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.sqlite_database import get_db, DATABASE_URL

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Check if the API and database are working"""
    try:
        # Test database connection
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "database": {
            "status": db_status,
            "type": "sqlite",
            "url": DATABASE_URL.split("://")[0]  # Don't show full path
        },
        "api_version": "1.0.0"
    }