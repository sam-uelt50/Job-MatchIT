from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import hashlib
import jwt
from datetime import datetime, timedelta
import sqlite3
import json
import uuid

app = FastAPI()

# CORS - Allow frontend on port 3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "jobmatch-secret-key-2024"
ALGORITHM = "HS256"

# Database setup
def init_db():
    conn = sqlite3.connect('job_recruitment.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE,
        password TEXT,
        name TEXT,
        type TEXT,
        profile TEXT
    )''')
    
    # Applications table
    cursor.execute('''CREATE TABLE IF NOT EXISTS applications (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        job_id TEXT,
        job_title TEXT,
        company_name TEXT,
        status TEXT,
        applied_at TEXT,
        messages TEXT
    )''')
    
    # Check if test user exists
    cursor.execute("SELECT * FROM users WHERE email = 'candidate@test.com'")
    if not cursor.fetchone():
        profile_data = {
            'full_name': 'Test Candidate',
            'email': 'candidate@test.com',
            'phone': '0912345678',
            'age': '25-30',
            'gender': 'Male',
            'location': 'Addis Ababa',
            'region': 'Addis Ababa',
            'city': 'Bole',
            'industry': 'technology',
            'skills': ['Python', 'JavaScript', 'React', 'Node.js'],
            'experience_years': 4,
            'experience_description': 'Full stack developer with 4 years experience building web applications.',
            'professional_summary': 'Experienced Full Stack Developer with strong problem-solving skills.',
            'projects': [],
            'education_details': [],
            'achievements': [],
            'certificates': [],
            'cv_name': None
        }
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
            ('user_001', 'candidate@test.com', hashlib.sha256('123456'.encode()).hexdigest(), 
             'Test Candidate', 'candidate', json.dumps(profile_data)))
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

init_db()

# ============ MODELS ============
class LoginRequest(BaseModel):
    email: str
    password: str

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[str] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    industry: Optional[str] = None
    skills: Optional[List[str]] = []
    experience_years: Optional[int] = 0
    experience_description: Optional[str] = None
    professional_summary: Optional[str] = None
    projects: Optional[List] = []
    education_details: Optional[List] = []
    achievements: Optional[List] = []
    certificates: Optional[List] = []
    cv_name: Optional[str] = None

class ApplyRequest(BaseModel):
    job_id: str
    job_title: str
    company_name: str

# ============ AUTH ENDPOINTS ============
@app.post("/api/auth/login")
async def login(request: LoginRequest):
    conn = sqlite3.connect('job_recruitment.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, password, name, type, profile FROM users WHERE email = ?", (request.email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or user[1] != hashlib.sha256(request.password.encode()).hexdigest():
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = jwt.encode(
        {"sub": user[0], "exp": datetime.utcnow() + timedelta(days=7)}, 
        SECRET_KEY, 
        algorithm=ALGORITHM
    )
    
    # Parse profile to get name
    profile = json.loads(user[4]) if user[4] else {}
    
    return {
        "access_token": token, 
        "user_id": user[0], 
        "name": profile.get('full_name', user[2]), 
        "user_type": user[3]
    }

# ============ PROFILE ENDPOINTS ============
@app.get("/api/user/profile")
async def get_profile():
    conn = sqlite3.connect('job_recruitment.db')
    cursor = conn.cursor()
    cursor.execute("SELECT profile FROM users WHERE id = 'user_001'")
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0]:
        return json.loads(result[0])
    return {"full_name": "Test Candidate", "email": "candidate@test.com", "skills": []}

@app.post("/api/user/profile")
async def update_profile(profile: ProfileUpdate):
    conn = sqlite3.connect('job_recruitment.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET profile = ? WHERE id = 'user_001'", (json.dumps(profile.dict()),))
    conn.commit()
    conn.close()
    return {"message": "Profile updated", "skills_count": len(profile.skills or [])}

# ============ JOB RECOMMENDATIONS ============
@app.get("/api/user/recommendations")
async def get_recommendations():
    # Full job listings with descriptions
    jobs = [
        {
            "job_id": "job_001", 
            "job_title": "Senior Full Stack Developer", 
            "company": "Zemen Tech", 
            "location": "Addis Ababa", 
            "job_type": "Full-time",
            "salary_range": "35,000 - 45,000 ETB",
            "experience_required": 4,
            "description": "We are seeking an experienced Full Stack Developer to join our core development team. You will be responsible for architecting and building scalable web applications, leading technical decisions, and mentoring junior developers.",
            "responsibilities": "Design and develop full-stack web applications\nLead code reviews and mentor team members\nOptimize application performance\nCollaborate with product managers",
            "required_skills": "Python, JavaScript, React, Node.js, SQL, Git",
            "required_education": "Bachelor's Degree in Computer Science",
            "hires_count": 2,
            "application_deadline": (datetime.now() + timedelta(days=15)).isoformat(),
            "days_left": 15,
            "is_expired": False,
            "match_score": 85,
            "skill_match": 82,
            "exp_match": 88,
            "nlp_match": 80,
            "missing_skills": ["Docker", "AWS"]
        },
        {
            "job_id": "job_002", 
            "job_title": "Frontend Developer (React)", 
            "company": "WebWorks Ethiopia", 
            "location": "Remote", 
            "job_type": "Contract",
            "salary_range": "25,000 - 30,000 ETB",
            "experience_required": 2,
            "description": "Looking for a talented Frontend Developer with strong React skills. You'll build responsive, user-friendly interfaces and integrate with backend APIs.",
            "responsibilities": "Build responsive UI components using React\nIntegrate REST APIs\nEnsure cross-browser compatibility\nOptimize application for speed",
            "required_skills": "React, JavaScript, HTML5, CSS3, Git",
            "required_education": "Bachelor's Degree or equivalent experience",
            "hires_count": 1,
            "application_deadline": (datetime.now() + timedelta(days=10)).isoformat(),
            "days_left": 10,
            "is_expired": False,
            "match_score": 78,
            "skill_match": 80,
            "exp_match": 75,
            "nlp_match": 72,
            "missing_skills": ["Tailwind CSS"]
        },
        {
            "job_id": "job_003", 
            "job_title": "Data Scientist", 
            "company": "Ethio Analytics", 
            "location": "Addis Ababa", 
            "job_type": "Full-time",
            "salary_range": "40,000 - 55,000 ETB",
            "experience_required": 3,
            "description": "Join our data science team to build predictive models and analytics solutions. You'll work with large datasets and implement machine learning algorithms.",
            "responsibilities": "Develop and deploy ML models\nPerform exploratory data analysis\nClean and preprocess datasets\nCreate data visualizations",
            "required_skills": "Python, SQL, Machine Learning, Pandas, Statistics",
            "required_education": "Master's Degree in Data Science",
            "hires_count": 1,
            "application_deadline": (datetime.now() + timedelta(days=20)).isoformat(),
            "days_left": 20,
            "is_expired": False,
            "match_score": 72,
            "skill_match": 68,
            "exp_match": 80,
            "nlp_match": 65,
            "missing_skills": ["TensorFlow", "PyTorch"]
        },
        {
            "job_id": "job_004", 
            "job_title": "DevOps Engineer", 
            "company": "CloudTech Solutions", 
            "location": "Addis Ababa", 
            "job_type": "Full-time",
            "salary_range": "38,000 - 48,000 ETB",
            "experience_required": 3,
            "description": "We are looking for a DevOps Engineer to manage our cloud infrastructure and automate deployment processes.",
            "responsibilities": "Manage AWS/GCP cloud infrastructure\nImplement CI/CD pipelines\nMonitor system performance\nAutomate deployment processes",
            "required_skills": "AWS, Docker, Kubernetes, Jenkins, Linux",
            "required_education": "Bachelor's Degree in Computer Science",
            "hires_count": 1,
            "application_deadline": (datetime.now() + timedelta(days=12)).isoformat(),
            "days_left": 12,
            "is_expired": False,
            "match_score": 65,
            "skill_match": 60,
            "exp_match": 75,
            "nlp_match": 58,
            "missing_skills": ["Terraform", "Ansible"]
        }
    ]
    return {"recommendations": jobs}

# ============ APPLY FOR JOB ============
@app.post("/api/user/apply/{job_id}")
async def apply_job(job_id: str):
    conn = sqlite3.connect('job_recruitment.db')
    cursor = conn.cursor()
    
    # Get job details from the jobs list
    jobs = [
        {"id": "job_001", "title": "Senior Full Stack Developer", "company": "Zemen Tech"},
        {"id": "job_002", "title": "Frontend Developer (React)", "company": "WebWorks Ethiopia"},
        {"id": "job_003", "title": "Data Scientist", "company": "Ethio Analytics"},
        {"id": "job_004", "title": "DevOps Engineer", "company": "CloudTech Solutions"}
    ]
    
    job_info = next((j for j in jobs if j["id"] == job_id), None)
    if not job_info:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if already applied
    cursor.execute("SELECT * FROM applications WHERE user_id = 'user_001' AND job_id = ?", (job_id,))
    existing = cursor.fetchone()
    if existing:
        return {"message": "Already applied", "already_applied": True}
    
    # Create new application
    app_id = str(uuid.uuid4())
    cursor.execute("""INSERT INTO applications 
        (id, user_id, job_id, job_title, company_name, status, applied_at, messages) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (app_id, 'user_001', job_id, job_info["title"], job_info["company"], 
         'pending', datetime.now().isoformat(), json.dumps([])))
    
    conn.commit()
    conn.close()
    
    return {"message": "Application submitted successfully", "application_id": app_id}

# ============ GET APPLICATIONS ============
@app.get("/api/user/applications")
async def get_applications():
    conn = sqlite3.connect('job_recruitment.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT job_id, job_title, company_name, status, applied_at, messages 
                      FROM applications WHERE user_id = 'user_001' ORDER BY applied_at DESC""")
    apps = cursor.fetchall()
    conn.close()
    
    # Add some sample applications if none exist
    if not apps:
        return {"applications": []}
    
    result = []
    for app in apps:
        result.append({
            "job_id": app[0],
            "job_title": app[1],
            "company_name": app[2],
            "status": app[3],
            "applied_at": app[4],
            "messages": json.loads(app[5]) if app[5] else []
        })
    
    return {"applications": result}

# ============ HEALTH CHECK ============
@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "JobMatch ET API Running!", "status": "ok", "endpoints": ["/api/auth/login", "/api/user/profile", "/api/user/recommendations", "/api/user/apply/{job_id}", "/api/user/applications"]}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting JobMatch ET Backend Server...")
    print("📍 API running at: http://localhost:8000")
    print("📍 Health check: http://localhost:8000/health")
    uvicorn.run(app, host="127.0.0.1", port=8000)