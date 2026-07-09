from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from typing import Optional, List
import uuid
import sqlite3
from datetime import datetime, timedelta
import os
import hashlib
import secrets
import jwt
import json
import re
import time

# Try to import Random Forest Matcher (optional)
try:
    from random_forest_matcher import rf_matcher
    RF_AVAILABLE = True
    print("✅ Random Forest matcher loaded successfully")
except ImportError as e:
    RF_AVAILABLE = False
    print(f"⚠️ Random Forest not available: {e}")
    # Create a dummy matcher
    class DummyMatcher:
        def __init__(self):
            self.categories = ['Technology', 'Finance', 'Business', 'Healthcare', 'Education', 'General']
        def predict_category(self, title, description):
            return {"category": "General", "confidence": 50, "method": "fallback"}
        def calculate_match_score_rf(self, *args, **kwargs):
            return {"match_score": 50, "skill_score": 50, "career_score": 50, "exp_score": 50, 
                    "rf_confidence": 50, "predicted_category": "General", "career_level": "Mid",
                    "exact_skill_matches": [], "semantic_matches": [], "missing_skills": [],
                    "skill_insights": ["Complete your profile for better matches"],
                    "career_insights": ["Add more experience details"], "analysis": "Profile analysis in progress"}
        def calculate_nlp_score(self, summary, title, desc):
            return {"score": 40, "insights": ["Add a detailed professional summary"], "common_keywords": []}
    rf_matcher = DummyMatcher()

app = FastAPI(title="JobMatch ET - AI Recruitment Platform")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database path - fixed to work from any directory
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'job_recruitment.db')

def get_db():
    max_retries = 3
    for i in range(max_retries):
        try:
            conn = sqlite3.connect(DB_PATH, timeout=30)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.OperationalError as e:
            if i == max_retries - 1:
                raise e
            time.sleep(0.5)

SECRET_KEY = "jobmatch-ethiopia-secret-key-2024"
ALGORITHM = "HS256"
security = HTTPBearer()

# ============ HASH FUNCTIONS ============
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
    return f"{salt}:{hashed}"

def verify_password(password: str, hashed_password: str) -> bool:
    try:
        salt, hash_value = hashed_password.split(':')
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest() == hash_value
    except:
        return False

def create_token(data: dict):
    expire = datetime.utcnow() + timedelta(days=7)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_token(credentials.credentials)
    return {"user_id": payload.get("sub"), "user_type": payload.get("user_type", "candidate")}

# ============ ENHANCED MATCH FUNCTION ============
def calculate_match_score_enhanced(user_skills, user_exp, user_summary, 
                                     job_skills_str, job_exp_req, 
                                     job_title, job_desc, job_type, 
                                     job_industry, user_location, 
                                     user_industry="", user_gpa=0):
    """Calculate match score using Random Forest"""
    
    # Get Random Forest match result
    rf_result = rf_matcher.calculate_match_score_rf(
        user_skills, user_exp, job_skills_str, job_exp_req,
        job_title, job_type, job_industry, user_location
    )
    
    # Get NLP score
    nlp_result = rf_matcher.calculate_nlp_score(user_summary, job_title, job_desc)
    
    # Combine scores
    final_score = (rf_result.get('match_score', 50) * 0.70) + (nlp_result.get('score', 40) * 0.30)
    final_score = round(final_score, 1)
    
    # Determine match level
    if final_score >= 85:
        category = "🏆 Excellent Match"
        color = "#28a745"
    elif final_score >= 70:
        category = "⭐ Great Match"
        color = "#17a2b8"
    elif final_score >= 55:
        category = "👍 Good Match"
        color = "#ffc107"
    elif final_score >= 40:
        category = "📌 Potential Match"
        color = "#fd7e14"
    else:
        category = "⚠️ Low Match"
        color = "#dc3545"
    
    return {
        "match_score": final_score,
        "category": category,
        "color": color,
        "skill_score": rf_result.get('skill_score', 0),
        "career_score": rf_result.get('career_score', 0),
        "exp_score": rf_result.get('exp_score', 0),
        "nlp_score": nlp_result.get('score', 0),
        "rf_confidence": rf_result.get('rf_confidence', 0),
        "predicted_category": rf_result.get('predicted_category', 'Unknown'),
        "career_level": rf_result.get('career_level', 'Not specified'),
        "exact_matches": rf_result.get('exact_skill_matches', []),
        "semantic_matches": rf_result.get('semantic_matches', []),
        "missing_skills": rf_result.get('missing_skills', []),
        "common_keywords": nlp_result.get('common_keywords', []),
        "analysis": rf_result.get('analysis', ''),
        "nlp_insights": nlp_result.get('insights', []),
        "skill_insights": rf_result.get('skill_insights', []),
        "career_insights": rf_result.get('career_insights', []),
        "explanation": f"Skills: {rf_result.get('skill_score', 0)}% | Career: {rf_result.get('career_score', 0)}% | NLP: {nlp_result.get('score', 0)}%"
    }

# ============ MODELS ============
class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str
    phone: Optional[str] = ""
    location: Optional[str] = ""

class CompanyRegister(BaseModel):
    email: str
    password: str
    company_name: str
    location: Optional[str] = ""

class LoginRequest(BaseModel):
    email: str
    password: str

class EducationEntry(BaseModel):
    degree: str
    field_of_study: str
    institution: str
    graduation_year: int
    gpa: Optional[float] = 0
    specialization: Optional[str] = ""

class ProfileUpdate(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = ""
    location: Optional[str] = ""
    region: Optional[str] = ""
    city: Optional[str] = ""
    industry: Optional[str] = ""
    skills: List[str] = []
    experience_years: int = 0
    experience_description: Optional[str] = ""
    professional_summary: Optional[str] = ""
    expected_salary: Optional[int] = 0
    linkedin_url: Optional[str] = ""
    portfolio_url: Optional[str] = ""
    education_details: Optional[List[EducationEntry]] = []
    projects: Optional[List[dict]] = []

class JobPost(BaseModel):
    title: str
    company_name: str
    location: str
    job_type: str = "Full-time"
    industry: Optional[str] = ""
    required_skills: str
    preferred_skills: Optional[str] = ""
    salary_range: Optional[str] = ""
    experience_required: int = 2
    required_education: Optional[str] = ""
    preferred_field_of_study: Optional[str] = ""
    min_gpa: Optional[float] = 0
    description: str
    responsibilities: Optional[str] = ""
    hires_count: Optional[int] = 1
    application_deadline: Optional[str] = ""

class CompanyProfileUpdate(BaseModel):
    company_name: str
    description: Optional[str] = ""
    website: Optional[str] = ""
    industry: Optional[str] = ""
    size: Optional[str] = ""
    founded_year: Optional[int] = None
    headquarters: Optional[str] = ""
    contact_email: Optional[str] = ""
    contact_phone: Optional[str] = ""

class MessageData(BaseModel):
    message: str

# ============ DATABASE INITIALIZATION ============
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY, email TEXT UNIQUE, password_hash TEXT, full_name TEXT, phone TEXT,
        location TEXT, region TEXT, city TEXT, skills TEXT, experience_years INTEGER,
        experience_description TEXT, professional_summary TEXT, industry TEXT, specialization TEXT,
        expected_salary INTEGER, education_details TEXT, projects TEXT, linkedin_url TEXT,
        portfolio_url TEXT, user_type TEXT DEFAULT 'candidate', created_at TEXT
    )''')
    
    # Jobs table
    cursor.execute('''CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY, title TEXT, company_name TEXT, location TEXT, job_type TEXT,
        industry TEXT, required_skills TEXT, preferred_skills TEXT, salary_range TEXT,
        experience_required INTEGER, description TEXT, responsibilities TEXT, benefits TEXT,
        required_education TEXT, preferred_field_of_study TEXT, min_gpa REAL DEFAULT 0,
        preferred_specialization TEXT, hires_count INTEGER DEFAULT 1,
        application_deadline TEXT, status TEXT, created_at TEXT, posted_by TEXT
    )''')
    
    # Applications table
    cursor.execute('''CREATE TABLE IF NOT EXISTS applications (
        id TEXT PRIMARY KEY, user_id TEXT, user_name TEXT, user_email TEXT, user_phone TEXT,
        user_location TEXT, user_skills TEXT, user_experience INTEGER, user_summary TEXT,
        user_gpa REAL, user_education TEXT, job_id TEXT, job_title TEXT, company_name TEXT,
        match_score INTEGER, skill_match INTEGER, exp_match INTEGER, nlp_match INTEGER,
        career_match INTEGER, rf_confidence REAL, predicted_category TEXT,
        exact_matches TEXT, missing_skills TEXT, analysis TEXT, 
        status TEXT DEFAULT 'pending', messages TEXT DEFAULT '[]', applied_at TEXT
    )''')
    
    # Company profiles table
    cursor.execute('''CREATE TABLE IF NOT EXISTS company_profiles (
        id TEXT PRIMARY KEY, user_id TEXT, company_name TEXT, description TEXT,
        website TEXT, industry TEXT, size TEXT, founded_year INTEGER,
        headquarters TEXT, contact_email TEXT, contact_phone TEXT, created_at TEXT
    )''')
    
    # Create test users
    cursor.execute("SELECT COUNT(*) FROM users WHERE email = 'candidate@test.com'")
    if cursor.fetchone()[0] == 0:
        test_user_id = str(uuid.uuid4())
        test_password_hash = hash_password("123456")
        cursor.execute('''INSERT INTO users (id, email, password_hash, full_name, phone, location, skills, experience_years, professional_summary, user_type, created_at) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (test_user_id, "candidate@test.com", test_password_hash, "Test Candidate", "0912345678", "Addis Ababa", "Python,JavaScript,React,HTML,CSS", 4, "Experienced full stack developer with 5+ years building web applications. Led teams of 5 developers.", "candidate", datetime.now().isoformat()))
        print("✅ Test candidate created")
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE email = 'company@test.com'")
    if cursor.fetchone()[0] == 0:
        test_company_id = str(uuid.uuid4())
        test_company_hash = hash_password("123456")
        cursor.execute('''INSERT INTO users (id, email, password_hash, full_name, location, user_type, created_at) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (test_company_id, "company@test.com", test_company_hash, "Test Company", "Addis Ababa", "company", datetime.now().isoformat()))
        print("✅ Test company created")
    
    # Add sample jobs
    cursor.execute("SELECT COUNT(*) FROM jobs")
    if cursor.fetchone()[0] == 0:
        sample_jobs = [
            ("1", "Senior Python Developer", "Tech Corp", "Remote", "Full-time", "Technology", "Python,Django,SQL,REST API", "Git,Docker", "120000-180000 ETB", 3, "Looking for experienced Python developer to build scalable backend services.", "Design APIs, Optimize queries", "Health insurance", "Bachelor's in CS", "Computer Science", 3.0, "Backend", 2, None, "active", None),
            ("2", "React Frontend Developer", "Innovate Solutions", "Remote", "Remote", "Technology", "React,JavaScript,HTML,CSS,Redux", "TypeScript,Tailwind", "100000-150000 ETB", 2, "Seeking React expert to build modern web applications.", "Build components, Optimize performance", "Flexible hours", "Bachelor's in CS", "Computer Science", 2.5, "Frontend", 1, None, "active", None),
            ("3", "Full Stack Developer", "WebWorks", "Remote", "Full-time", "Technology", "Python,React,JavaScript,Node.js,MongoDB", "Express,PostgreSQL", "130000-190000 ETB", 3, "Full stack developer needed for end-to-end development.", "Develop features, Code reviews", "Stock options", "Bachelor's in CS", "Computer Science", 2.8, "Full Stack", 3, None, "active", None)
        ]
        for job in sample_jobs:
            cursor.execute('''INSERT INTO jobs (id, title, company_name, location, job_type, industry, required_skills, preferred_skills, salary_range, experience_required, description, responsibilities, benefits, required_education, preferred_field_of_study, min_gpa, preferred_specialization, hires_count, application_deadline, status, created_at, posted_by) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?)''', job)
        print("✅ Sample jobs added")
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

init_db()

# ============ AUTH ROUTES ============
@app.post("/api/auth/register/user")
async def register_user(data: UserRegister):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (data.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = str(uuid.uuid4())
    password_hash = hash_password(data.password)
    cursor.execute('''INSERT INTO users (id, email, password_hash, full_name, phone, location, user_type, created_at) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                   (user_id, data.email, password_hash, data.full_name, data.phone, data.location, "candidate", datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return {"access_token": create_token({"sub": user_id, "user_type": "candidate"}), "user_id": user_id, "name": data.full_name, "user_type": "candidate"}

@app.post("/api/auth/register/company")
async def register_company(data: CompanyRegister):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (data.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = str(uuid.uuid4())
    password_hash = hash_password(data.password)
    cursor.execute('''INSERT INTO users (id, email, password_hash, full_name, location, user_type, created_at) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (user_id, data.email, password_hash, data.company_name, data.location, "company", datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return {"access_token": create_token({"sub": user_id, "user_type": "company"}), "user_id": user_id, "name": data.company_name, "user_type": "company"}

@app.post("/api/auth/login")
async def login(data: LoginRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name, password_hash, user_type FROM users WHERE email = ?", (data.email,))
    user = cursor.fetchone()
    if user and verify_password(data.password, user[2]):
        conn.close()
        return {"access_token": create_token({"sub": user[0], "user_type": user[3]}), "user_id": user[0], "name": user[1], "user_type": user[3]}
    conn.close()
    raise HTTPException(status_code=401, detail="Invalid credentials")

# ============ PROFILE ROUTES ============
@app.post("/api/user/profile")
async def update_profile(profile: ProfileUpdate, current_user: dict = Depends(get_current_user)):
    if current_user.get("user_type") != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can update profile")
    
    conn = get_db()
    cursor = conn.cursor()
    skills_str = ','.join(profile.skills)
    education_json = json.dumps([edu.dict() for edu in profile.education_details]) if profile.education_details else "[]"
    projects_json = json.dumps(profile.projects) if profile.projects else "[]"
    
    cursor.execute('''UPDATE users SET full_name=?, phone=?, location=?, region=?, city=?, industry=?,
                   skills=?, experience_years=?, experience_description=?, professional_summary=?,
                   expected_salary=?, linkedin_url=?, portfolio_url=?, education_details=?, projects=?
                   WHERE id=?''',
                   (profile.full_name, profile.phone, profile.location, profile.region, profile.city,
                    profile.industry, skills_str, profile.experience_years, profile.experience_description,
                    profile.professional_summary, profile.expected_salary, profile.linkedin_url,
                    profile.portfolio_url, education_json, projects_json, current_user["user_id"]))
    
    conn.commit()
    conn.close()
    return {"message": "Profile updated", "skills_count": len(profile.skills)}

@app.get("/api/user/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    if current_user.get("user_type") != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can view profile")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''SELECT full_name, email, phone, location, region, city, industry, skills,
                      experience_years, experience_description, professional_summary, expected_salary,
                      linkedin_url, portfolio_url, education_details, projects
                      FROM users WHERE id=?''', (current_user["user_id"],))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return {"full_name": "", "email": "", "skills": []}
    
    return {
        "full_name": user[0] or "", "email": user[1] or "", "phone": user[2] or "",
        "location": user[3] or "", "region": user[4] or "", "city": user[5] or "",
        "industry": user[6] or "", "skills": user[7].split(',') if user[7] else [],
        "experience_years": user[8] or 0, "experience_description": user[9] or "",
        "professional_summary": user[10] or "", "expected_salary": user[11] or 0,
        "linkedin_url": user[12] or "", "portfolio_url": user[13] or "",
        "education_details": json.loads(user[14]) if user[14] else [],
        "projects": json.loads(user[15]) if user[15] else []
    }

# ============ COMPANY PROFILE ROUTES ============
@app.post("/api/company/profile")
async def update_company_profile(profile: CompanyProfileUpdate, current_user: dict = Depends(get_current_user)):
    if current_user.get("user_type") != "company":
        raise HTTPException(status_code=403, detail="Only companies can update profile")
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM company_profiles WHERE user_id = ?", (current_user["user_id"],))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute('''UPDATE company_profiles 
                       SET company_name=?, description=?, website=?, industry=?, size=?, 
                           founded_year=?, headquarters=?, contact_email=?, contact_phone=?
                       WHERE user_id=?''',
                       (profile.company_name, profile.description, profile.website, profile.industry, 
                        profile.size, profile.founded_year, profile.headquarters, profile.contact_email, 
                        profile.contact_phone, current_user["user_id"]))
    else:
        cursor.execute('''INSERT INTO company_profiles (id, user_id, company_name, description, website, industry, size, founded_year, headquarters, contact_email, contact_phone, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (str(uuid.uuid4()), current_user["user_id"], profile.company_name, profile.description, 
                        profile.website, profile.industry, profile.size, profile.founded_year, profile.headquarters,
                        profile.contact_email, profile.contact_phone, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    return {"message": "Company profile updated"}

@app.get("/api/company/profile")
async def get_company_profile(current_user: dict = Depends(get_current_user)):
    if current_user.get("user_type") != "company":
        raise HTTPException(status_code=403, detail="Only companies can view profile")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM company_profiles WHERE user_id = ?", (current_user["user_id"],))
    profile = cursor.fetchone()
    conn.close()
    
    if not profile:
        return {"company_name": "", "description": ""}
    
    return dict(profile)

# ============ COMPANY JOB ROUTES ============
@app.post("/api/company/jobs")
async def create_job(job: JobPost, current_user: dict = Depends(get_current_user)):
    if current_user.get("user_type") != "company":
        raise HTTPException(status_code=403, detail="Only companies can post jobs")
    
    conn = get_db()
    cursor = conn.cursor()
    job_id = str(uuid.uuid4())
    
    rf_prediction = rf_matcher.predict_category(job.title, job.description)
    
    cursor.execute('''INSERT INTO jobs (id, title, company_name, location, job_type, industry,
                   required_skills, preferred_skills, salary_range, experience_required,
                   required_education, preferred_field_of_study, min_gpa, description,
                   responsibilities, hires_count, application_deadline, status, created_at, posted_by) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (job_id, job.title, job.company_name, job.location, job.job_type,
                    rf_prediction.get('category', job.industry) if not job.industry else job.industry,
                    job.required_skills, job.preferred_skills, job.salary_range,
                    job.experience_required, job.required_education, job.preferred_field_of_study,
                    job.min_gpa, job.description, job.responsibilities, job.hires_count,
                    job.application_deadline, 'active', datetime.now().isoformat(), current_user["user_id"]))
    
    conn.commit()
    conn.close()
    return {"message": "Job posted successfully", "job_id": job_id, "ai_category": rf_prediction.get('category', 'General')}

@app.get("/api/company/jobs")
async def get_company_jobs(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE posted_by=? ORDER BY created_at DESC", (current_user["user_id"],))
    jobs = cursor.fetchall()
    conn.close()
    return {"jobs": [dict(job) for job in jobs]}

@app.get("/api/company/applications")
async def get_company_applications(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''SELECT a.* FROM applications a JOIN jobs j ON a.job_id=j.id 
                   WHERE j.posted_by=? ORDER BY a.match_score DESC''', (current_user["user_id"],))
    apps = cursor.fetchall()
    conn.close()
    result = []
    for i, app in enumerate(apps):
        app_dict = dict(app)
        app_dict["rank"] = i + 1
        if app_dict.get("messages"):
            try:
                app_dict["messages"] = json.loads(app_dict["messages"])
            except:
                app_dict["messages"] = []
        result.append(app_dict)
    return {"applications": result}

@app.put("/api/company/applications/{application_id}/status")
async def update_application_status(application_id: str, status: str, current_user: dict = Depends(get_current_user)):
    if current_user.get("user_type") != "company":
        raise HTTPException(status_code=403, detail="Only companies can update status")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE applications SET status=? WHERE id=?", (status, application_id))
    conn.commit()
    conn.close()
    return {"message": f"Status updated to {status}"}

@app.post("/api/company/applications/{application_id}/message")
async def send_message(application_id: str, message_data: MessageData, current_user: dict = Depends(get_current_user)):
    if current_user.get("user_type") != "company":
        raise HTTPException(status_code=403, detail="Only companies can send messages")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT messages FROM applications WHERE id=?", (application_id,))
    row = cursor.fetchone()
    messages = json.loads(row[0]) if row and row[0] else []
    messages.append({"message": message_data.message, "sent_at": datetime.now().isoformat(), "from": "company"})
    cursor.execute("UPDATE applications SET messages=? WHERE id=?", (json.dumps(messages), application_id))
    conn.commit()
    conn.close()
    return {"message": "Message sent"}

# ============ CANDIDATE ROUTES ============
@app.get("/api/user/recommendations")
async def get_recommendations(current_user: dict = Depends(get_current_user), limit: int = 50):
    if current_user.get("user_type") != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can get recommendations")
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT skills, experience_years, professional_summary, industry, location, education_details FROM users WHERE id=?", (current_user["user_id"],))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return {"user": {"skills": []}, "recommendations": []}
    
    user_skills = user[0].split(',') if user[0] else []
    user_exp = user[1] or 0
    user_summary = user[2] or ""
    user_industry = user[3] or ""
    user_location = user[4] or ""
    user_education = json.loads(user[5]) if user[5] else []
    user_gpa = max([edu.get("gpa", 0) for edu in user_education]) if user_education else 0
    
    cursor.execute("SELECT id, title, company_name, location, job_type, industry, required_skills, experience_required, description FROM jobs WHERE status='active'")
    jobs = cursor.fetchall()
    conn.close()
    
    recommendations = []
    for job in jobs:
        match = calculate_match_score_enhanced(
            user_skills, user_exp, user_summary,
            job["required_skills"] or "", job["experience_required"] or 2,
            job["title"] or "", job["description"] or "",
            job["job_type"] or "Full-time",
            job["industry"] or user_industry,
            user_location, user_industry, user_gpa
        )
        
        recommendations.append({
            "job_id": job["id"],
            "job_title": job["title"],
            "company": job["company_name"],
            "location": job["location"] or "Remote",
            "job_type": job["job_type"] or "Full-time",
            "salary_range": "Negotiable",
            "experience_required": job["experience_required"] or 2,
            "required_skills": job["required_skills"] or "",
            "match_score": match["match_score"],
            "category": match["category"],
            "color": match["color"],
            "skill_match": match["skill_score"],
            "career_match": match["career_score"],
            "exp_match": match["exp_score"],
            "nlp_match": match["nlp_score"],
            "rf_confidence": match.get("rf_confidence"),
            "predicted_category": match.get("predicted_category"),
            "career_level": match.get("career_level"),
            "exact_matches": match.get("exact_matches", []),
            "semantic_matches": match.get("semantic_matches", []),
            "missing_skills": match.get("missing_skills", []),
            "analysis": match.get("analysis", ""),
            "skill_insights": match.get("skill_insights", []),
            "career_insights": match.get("career_insights", []),
            "nlp_insights": match.get("nlp_insights", []),
            "explanation": match["explanation"]
        })
    
    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    
    return {
        "user": {"skills": user_skills, "experience_years": user_exp, "gpa": user_gpa},
        "recommendations": recommendations[:limit],
        "ml_model": "AI Enhanced",
        "total_jobs": len(jobs)
    }

@app.post("/api/user/apply/{job_id}")
async def apply_for_job(job_id: str, current_user: dict = Depends(get_current_user)):
    if current_user.get("user_type") != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can apply")
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT full_name, email, phone, location, skills, experience_years, professional_summary, industry, education_details FROM users WHERE id=?", (current_user["user_id"],))
    user = cursor.fetchone()
    
    cursor.execute("SELECT title, company_name, required_skills, experience_required, description, job_type, industry, location FROM jobs WHERE id=?", (job_id,))
    job = cursor.fetchone()
    
    if not job:
        conn.close()
        raise HTTPException(status_code=404, detail="Job not found")
    
    user_skills = user[4].split(',') if user[4] else []
    user_exp = user[5] or 0
    user_summary = user[6] or ""
    user_industry = user[7] or ""
    user_education = json.loads(user[8]) if user[8] else []
    user_gpa = max([edu.get("gpa", 0) for edu in user_education]) if user_education else 0
    
    match = calculate_match_score_enhanced(
        user_skills, user_exp, user_summary,
        job[2] or "", job[3] or 2,
        job[0] or "", job[4] or "",
        job[5] or "Full-time",
        job[6] or user_industry,
        user[3] or "", user_industry, user_gpa
    )
    
    cursor.execute("SELECT id FROM applications WHERE user_id=? AND job_id=?", (current_user["user_id"], job_id))
    if cursor.fetchone():
        conn.close()
        return {"message": "Already applied", "match_score": match["match_score"]}
    
    app_id = str(uuid.uuid4())
    cursor.execute('''INSERT INTO applications (id, user_id, user_name, user_email, user_phone, user_location,
                   user_skills, user_experience, user_summary, user_gpa, user_education, job_id, 
                   job_title, company_name, match_score, skill_match, exp_match, nlp_match,
                   career_match, rf_confidence, predicted_category, exact_matches, missing_skills, analysis, status, applied_at) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (app_id, current_user["user_id"], user[0], user[1], user[2], user[3],
                    user[4], user_exp, user_summary, user_gpa, json.dumps(user_education),
                    job_id, job[0], job[1], match["match_score"], match["skill_score"], 
                    match["exp_score"], match["nlp_score"], match["career_score"],
                    match.get("rf_confidence"), match.get("predicted_category"),
                    json.dumps(match.get("exact_matches", [])), json.dumps(match.get("missing_skills", [])),
                    match.get("analysis", ""), "pending", datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    return {"message": f"Applied for {job[0]}", "application_id": app_id, "match_score": match["match_score"]}

@app.get("/api/user/applications")
async def get_applications(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications WHERE user_id=? ORDER BY applied_at DESC", (current_user["user_id"],))
    apps = cursor.fetchall()
    conn.close()
    
    result = []
    for app in apps:
        app_dict = dict(app)
        if app_dict.get("messages"):
            try:
                app_dict["messages"] = json.loads(app_dict["messages"])
            except:
                app_dict["messages"] = []
        if app_dict.get("exact_matches"):
            try:
                app_dict["exact_matches"] = json.loads(app_dict["exact_matches"])
            except:
                app_dict["exact_matches"] = []
        if app_dict.get("missing_skills"):
            try:
                app_dict["missing_skills"] = json.loads(app_dict["missing_skills"])
            except:
                app_dict["missing_skills"] = []
        result.append(app_dict)
    
    return {"applications": result}

# ============ ML STATUS ENDPOINTS ============
@app.get("/api/ml/status")
async def get_ml_status():
    return {
        "random_forest_available": RF_AVAILABLE,
        "ml_model": "Random Forest Enhanced with NLP",
        "version": "2.0",
        "categories": rf_matcher.categories
    }

@app.post("/api/ml/predict-category")
async def predict_category(data: dict):
    title = data.get("title", "")
    description = data.get("description", "")
    result = rf_matcher.predict_category(title, description)
    return result

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "ml_enabled": RF_AVAILABLE}

@app.get("/")
async def root():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM jobs")
    jobs = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users WHERE user_type='candidate'")
    candidates = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users WHERE user_type='company'")
    companies = cursor.fetchone()[0]
    conn.close()
    return {
        "message": "JobMatch ET API Running with AI",
        "jobs": jobs,
        "candidates": candidates,
        "companies": companies,
        "ml_enabled": RF_AVAILABLE,
        "ml_model": "AI Enhanced"
    }

# For direct execution
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)