
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, Float
from datetime import datetime
from app.core.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    skills = Column(Text, nullable=True)
    experience_years = Column(Integer, default=0)
    resume_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    company_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    industry = Column(String, nullable=True)
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    company_id = Column(String, nullable=False)
    company_name = Column(String, nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    salary_range = Column(String, nullable=True)
    employment_type = Column(String, default="full-time")
    is_remote = Column(Boolean, default=True)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False)
    user_name = Column(String, nullable=True)
    user_email = Column(String, nullable=True)
    user_skills = Column(Text, nullable=True)
    user_experience = Column(Integer, default=0)
    job_id = Column(String, nullable=False)
    job_title = Column(String, nullable=True)
    company_id = Column(String, nullable=False)
    company_name = Column(String, nullable=True)
    match_score = Column(Float, default=0)
    rank_category = Column(String, default="Pending")
    status = Column(String, default="applied")
    applied_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)