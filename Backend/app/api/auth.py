from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import uuid
from jose import jwt
import bcrypt
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User, Company

router = APIRouter(prefix="/api/auth", tags=["auth"])

SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"

# ============ PYDANTIC MODELS ============

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    location: Optional[str] = None

class CompanyRegister(BaseModel):
    company_name: str
    email: EmailStr
    password: str
    industry: Optional[str] = None
    location: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# ============ PASSWORD HASHING FUNCTIONS ============

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# ============ TOKEN FUNCTIONS ============

def create_token(user_id: str, user_type: str):
    """Create JWT token"""
    expire = datetime.utcnow() + timedelta(days=1)
    return jwt.encode({"sub": user_id, "type": user_type, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

# ============ AUTH ENDPOINTS ============

@router.post("/register/user")
async def register_user(data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user (job seeker)"""
    try:
        # Check if user exists
        result = await db.execute(select(User).where(User.email == data.email))
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            phone=data.phone,
            location=data.location
        )
        db.add(user)
        await db.commit()
        
        return {
            "access_token": create_token(user_id, "user"),
            "user_id": user_id,
            "user_type": "user",
            "email": data.email,
            "name": data.full_name,
            "message": "Registration successful"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/register/company")
async def register_company(data: CompanyRegister, db: AsyncSession = Depends(get_db)):
    """Register a new company (employer)"""
    try:
        # Check if company exists
        result = await db.execute(select(Company).where(Company.email == data.email))
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new company
        company_id = str(uuid.uuid4())
        company = Company(
            id=company_id,
            company_name=data.company_name,
            email=data.email,
            hashed_password=hash_password(data.password),
            industry=data.industry,
            location=data.location
        )
        db.add(company)
        await db.commit()
        
        return {
            "access_token": create_token(company_id, "company"),
            "user_id": company_id,
            "user_type": "company",
            "email": data.email,
            "name": data.company_name,
            "message": "Company registered successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login as user or company"""
    try:
        # Check user
        result = await db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()
        if user and verify_password(data.password, user.hashed_password):
            return {
                "access_token": create_token(user.id, "user"),
                "user_id": user.id,
                "user_type": "user",
                "email": user.email,
                "name": user.full_name,
                "message": "Login successful"
            }
        
        # Check company
        result = await db.execute(select(Company).where(Company.email == data.email))
        company = result.scalar_one_or_none()
        if company and verify_password(data.password, company.hashed_password):
            return {
                "access_token": create_token(company.id, "company"),
                "user_id": company.id,
                "user_type": "company",
                "email": company.email,
                "name": company.company_name,
                "message": "Login successful"
            }
        
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me")
async def get_current_user(token: str, db: AsyncSession = Depends(get_db)):
    """Get current user info from token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        user_type = payload.get("type")
        
        if user_type == "user":
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                return {
                    "id": user.id,
                    "email": user.email,
                    "name": user.full_name,
                    "type": "user",
                    "phone": user.phone,
                    "location": user.location
                }
        elif user_type == "company":
            result = await db.execute(select(Company).where(Company.id == user_id))
            company = result.scalar_one_or_none()
            if company:
                return {
                    "id": company.id,
                    "email": company.email,
                    "name": company.company_name,
                    "type": "company",
                    "industry": company.industry,
                    "location": company.location
                }
        
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))