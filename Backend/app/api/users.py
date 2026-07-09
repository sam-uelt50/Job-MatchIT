from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from app.core.database import get_database

router = APIRouter()

@router.get("/")
async def get_users(db=Depends(get_database)):
    users = await db.users.find({}).to_list(length=100)
    for user in users:
        user["id"] = str(user["_id"])
        del user["_id"]
        if "hashed_password" in user:
            del user["hashed_password"]
    return {"users": users}
