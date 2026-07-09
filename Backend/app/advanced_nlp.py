
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

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'job_recruitment.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE,
        password_hash TEXT,
        full_name TEXT,
        phone TEXT,
        location TEXT,
        region TEXT,
        city TEXT,
        title TEXT,
        preferred_title TEXT,
        professional_summary TEXT,
        industry_sector TEXT,
        specialization_area TEXT,
        professional_license TEXT,
        license_number TEXT,
        skills TEXT,
        experience_years INTEGER,
        years_in_ethiopia INTEGER,
        expected_salary INTEGER,
        employment_type TEXT,
        willing_to_relocate TEXT,
        notice_period INTEGER,
        linkedin_url TEXT,
        github_url TEXT,
        portfolio_url TEXT,
        experience_data TEXT,
        education_data TEXT,
        certification_data TEXT,
        achievement_data TEXT,
        language_data TEXT,
        volunteer_work TEXT,
        publications TEXT,
        memberships TEXT,
        reference_name TEXT,
        reference_phone TEXT,
        reference_email TEXT,
        reference_relation TEXT,
        created_at TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        title TEXT,
        company_name TEXT,
        location TEXT,
        required_skills TEXT,
        salary_range TEXT,
        experience_required INTEGER,
        industry_sector TEXT,
        specialization_area TEXT,
        required_education TEXT,
        required_certifications TEXT,
        employment_type TEXT,
        required_languages TEXT,
        required_software TEXT,
        description TEXT,
        status TEXT,
        created_at TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS applications (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        user_name TEXT,
        job_id TEXT,
        job_title TEXT,
        company_name TEXT,
        match_score INTEGER,
        match_breakdown TEXT,
        status TEXT,
        applied_at TEXT
    )''')
    
    # Add sample jobs
    cursor.execute("SELECT COUNT(*) FROM jobs")
    if cursor.fetchone()[0] == 0:
        sample_jobs = [
            ("1", "Senior Python Developer", "Tech Corp", "Remote", "Python,Django,SQL,REST APIs,FastAPI", "120000-180000 ETB", 3, "Technology", "Backend", "Bachelor's Degree in CS", "AWS Certified, Python Certification", "Full-time", "English", "Git,Docker,AWS", "Looking for experienced Python developer for backend services"),
            ("2", "React Frontend Developer", "Innovate Solutions", "Remote", "React,JavaScript,HTML,CSS,Redux,TypeScript", "100000-150000 ETB", 2, "Technology", "Frontend", "Bachelor's Degree", "React Certified", "Full-time", "English", "Figma,Webpack", "React expert needed for modern web apps"),
            ("3", "Full Stack Developer", "WebWorks", "Remote", "Python,React,JavaScript,Node.js,MongoDB,Express", "130000-190000 ETB", 3, "Technology", "Full Stack", "Bachelor's Degree in CS/IT", "Full Stack Certification", "Remote", "English", "Git,Docker", "Full stack developer for end-to-end development"),
            ("4", "Data Scientist", "AI Analytics", "Remote", "Python,Machine Learning,SQL,Statistics,TensorFlow", "140000-200000 ETB", 3, "Technology", "Data Science", "Master's Degree", "ML Certification", "Remote", "English", "Jupyter,Tableau", "Data scientist for ML projects"),
            ("5", "DevOps Engineer", "Cloud Services", "Remote", "AWS,Docker,Kubernetes,CI/CD,Linux,Terraform", "130000-180000 ETB", 4, "Technology", "DevOps", "Bachelor's Degree", "AWS Certified, CKA", "Remote", "English", "Terraform,Ansible", "DevOps engineer for cloud infrastructure")
        ]
        for job in sample_jobs:
            cursor.execute('''INSERT INTO jobs (id, title, company_name, location, required_skills, salary_range, experience_required, industry_sector, specialization_area, required_education, required_certifications, employment_type, required_languages, required_software, description, status, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (job[0], job[1], job[2], job[3], job[4], job[5], job[6], job[7], job[8], job[9], job[10], job[11], job[12], job[13], job[14], 'active', datetime.now().isoformat()))
        print("Sample jobs added")
    
    conn.commit()
    conn.close()
    print("Database initialized")

init_db()

SECRET_KEY = "ethiopian-job-secret-key"
ALGORITHM = "HS256"
security = HTTPBearer()

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    return f"{salt}:{hashlib.sha256(f'{password}{salt}'.encode()).hexdigest()}"

def verify_password(password: str, hashed: str) -> bool:
    try:
        salt, hash_value = hashed.split(':')
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest() == hash_value
    except:
        return False

def create_token(user_id: str):
    expire = datetime.utcnow() + timedelta(days=1)
    return jwt.encode({"sub": user_id, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_token(credentials.credentials)
    return {"user_id": payload.get("sub")}

# ============ MODELS ============
class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str
    phone: Optional[str] = None
    location: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

# ============ ADVANCED CV SCORING ENGINE ============
class AdvancedCVAnalyzer:
    def __init__(self):
        self.tech_skills_db = {
            'programming': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'php'],
            'web_frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 'rails', 'laravel'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'redis', 'firebase', 'cassandra'],
            'cloud_devops': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform', 'ansible', 'ci/cd'],
            'data_science': ['tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'tableau', 'power bi']
        }
    
    def analyze_experience_depth(self, experience_data):
        if not experience_data:
            return {"score": 0, "total_years": 0, "achievement_count": 0}
        
        total_years = 0
        achievement_count = 0
        
        for exp in experience_data:
            start = exp.get('start_date', '')
            end = exp.get('end_date', '')
            if start and end:
                try:
                    start_year = int(start.split('-')[0])
                    end_year = int(end.split('-')[0]) if end != 'present' else 2025
                    total_years += (end_year - start_year)
                except:
                    pass
            
            achievements = exp.get('achievements', '')
            if achievements:
                achievement_count += len(re.findall(r'[•\-*\d+]', achievements)) + 1
        
        experience_score = min(100, total_years * 15 + achievement_count * 5)
        return {"score": experience_score, "total_years": total_years, "achievement_count": achievement_count}
    
    def analyze_education_quality(self, education_data):
        if not education_data:
            return {"score": 0, "highest_degree": "Not specified"}
        
        edu_scores = []
        for edu in education_data:
            degree = edu.get('degree', '').lower()
            if 'phd' in degree or 'doctorate' in degree:
                degree_score = 100
            elif 'master' in degree:
                degree_score = 85
            elif 'bachelor' in degree:
                degree_score = 70
            elif 'diploma' in degree:
                degree_score = 55
            else:
                degree_score = 40
            edu_scores.append(degree_score)
        
        avg_score = sum(edu_scores) / len(edu_scores) if edu_scores else 0
        return {"score": avg_score, "highest_degree": education_data[0].get('degree', 'Not specified') if education_data else "Not specified"}
    
    def analyze_certifications_quality(self, certification_data):
        if not certification_data:
            return {"score": 0, "cert_count": 0}
        
        high_value_certs = ['aws', 'azure', 'google cloud', 'pmp', 'scrum master', 'tensorflow', 'kubernetes', 'docker', 'cisco']
        total_score = 0
        
        for cert in certification_data:
            name = cert.get('name', '').lower()
            base_score = 50
            if any(hv in name for hv in high_value_certs):
                base_score += 30
            total_score += min(100, base_score)
        
        avg_score = total_score / len(certification_data) if certification_data else 0
        return {"score": avg_score, "cert_count": len(certification_data)}
    
    def analyze_achievements_impact(self, achievement_data, publications):
        impact_score = 0
        if achievement_data:
            for ach in achievement_data:
                ach_text = ach if isinstance(ach, str) else ach.get('text', '')
                ach_lower = ach_text.lower()
                if any(word in ach_lower for word in ['award', 'winner', 'best', 'excellence']):
                    impact_score += 30
                elif any(word in ach_lower for word in ['published', 'paper', 'research']):
                    impact_score += 25
                elif any(char.isdigit() for char in ach_text):
                    impact_score += 15
                else:
                    impact_score += 10
        
        if publications:
            impact_score += 30
        
        return {"score": min(100, impact_score + 20), "achievement_count": len(achievement_data) if achievement_data else 0}
    
    def analyze_language_skills(self, language_data):
        if not language_data:
            return {"score": 0, "language_count": 0}
        
        proficiency_map = {'native': 100, 'fluent': 90, 'advanced': 75, 'intermediate': 60, 'basic': 40}
        total_score = 0
        
        for lang in language_data:
            proficiency = lang.get('proficiency', '').lower()
            score = proficiency_map.get(proficiency, 50)
            total_score += score
        
        avg_score = total_score / len(language_data) if language_data else 0
        return {"score": avg_score, "language_count": len(language_data)}
    
    def calculate_cv_completeness(self, profile):
        required_fields = ['full_name', 'email', 'phone', 'location', 'title', 'professional_summary', 'skills', 'experience_data', 'education_data']
        optional_fields = ['certification_data', 'achievement_data', 'language_data', 'volunteer_work', 'publications', 'memberships']
        
        filled_required = sum(1 for f in required_fields if profile.get(f))
        filled_optional = sum(1 for f in optional_fields if profile.get(f))
        
        required_score = (filled_required / len(required_fields)) * 60
        optional_score = (filled_optional / len(optional_fields)) * 40
        return min(100, required_score + optional_score)
    
    def calculate_comprehensive_score(self, candidate, job):
        scores = {}
        
        # 1. Skills Match (25%)
        candidate_skills = [s.lower() for s in candidate.get('skills', [])]
        job_skills = [s.strip().lower() for s in job.get('required_skills', '').split(',')] if job.get('required_skills') else []
        if job_skills and candidate_skills:
            matched = sum(1 for js in job_skills if js in candidate_skills)
            skills_score = (matched / len(job_skills)) * 100
        else:
            skills_score = 0
        scores['skills'] = skills_score * 0.25
        
        # 2. Experience Depth (15%)
        exp_analysis = self.analyze_experience_depth(candidate.get('experience_data', []))
        scores['experience'] = exp_analysis['score'] * 0.15
        
        # 3. Education Quality (10%)
        edu_analysis = self.analyze_education_quality(candidate.get('education_data', []))
        scores['education'] = edu_analysis['score'] * 0.10
        
        # 4. Certifications (10%)
        cert_analysis = self.analyze_certifications_quality(candidate.get('certification_data', []))
        scores['certifications'] = cert_analysis['score'] * 0.10
        
        # 5. Achievements (8%)
        ach_analysis = self.analyze_achievements_impact(candidate.get('achievement_data', []), candidate.get('publications', ''))
        scores['achievements'] = ach_analysis['score'] * 0.08
        
        # 6. Languages (5%)
        lang_analysis = self.analyze_language_skills(candidate.get('language_data', []))
        scores['languages'] = lang_analysis['score'] * 0.05
        
        # 7. Industry Alignment (10%)
        candidate_industry = candidate.get('industry_sector', '').lower()
        job_industry = job.get('industry_sector', '').lower()
        if candidate_industry and job_industry:
            industry_score = 100 if candidate_industry == job_industry else 30
        else:
            industry_score = 50
        scores['industry'] = industry_score * 0.10
        
        # 8. CV Completeness (7%)
        completeness_score = self.calculate_cv_completeness(candidate)
        scores['completeness'] = completeness_score * 0.07
        
        # 9. Salary Alignment (5%)
        candidate_salary = candidate.get('expected_salary', 0)
        job_salary = job.get('salary_range', '')
        salary_score = 50
        if candidate_salary > 0 and job_salary:
            numbers = re.findall(r'\d+', job_salary)
            if numbers:
                avg_salary = sum(int(n) for n in numbers) / len(numbers)
                if candidate_salary <= avg_salary:
                    salary_score = 100
                elif candidate_salary <= avg_salary * 1.2:
                    salary_score = 80
                else:
                    salary_score = 50
        scores['salary'] = salary_score * 0.05
        
        # 10. Location & Relocation (5%)
        job_location = job.get('location', '').lower()
        candidate_location = candidate.get('location', '').lower()
        willing_relocate = candidate.get('willing_to_relocate', 'No').lower()
        if job_location == 'remote':
            location_score = 100
        elif candidate_location and job_location and candidate_location in job_location:
            location_score = 100
        elif willing_relocate == 'yes':
            location_score = 80
        else:
            location_score = 50
        scores['location'] = location_score * 0.05
        
        total_score = sum(scores.values())
        total_score = min(100, max(0, round(total_score)))
        
        if total_score >= 80:
            category = "🏆 Excellent Match"
            color = "#28a745"
        elif total_score >= 65:
            category = "⭐ Great Match"
            color = "#17a2b8"
        elif total_score >= 50:
            category = "👍 Good Match"
            color = "#ffc107"
        elif total_score >= 35:
            category = "📌 Potential Match"
            color = "#fd7e14"
        else:
            category = "⚠️ Low Match"
            color = "#dc3545"
        
        return {
            "match_score": total_score,
            "category": category,
            "color": color,
            "breakdown": {
                "skills": round(skills_score, 1),
                "experience_depth": round(exp_analysis['score'], 1),
                "education_quality": round(edu_analysis['score'], 1),
                "certifications": round(cert_analysis['score'], 1),
                "achievements": round(ach_analysis['score'], 1),
                "languages": round(lang_analysis['score'], 1),
                "industry_alignment": round(industry_score, 1),
                "cv_completeness": round(completeness_score, 1),
                "salary_fit": round(salary_score, 1),
                "location_fit": round(location_score, 1)
            },
            "details": {
                "experience_years": exp_analysis.get('total_years', 0),
                "achievement_count": exp_analysis.get('achievement_count', 0),
                "highest_degree": edu_analysis.get('highest_degree', ''),
                "certification_count": cert_analysis.get('cert_count', 0),
                "language_count": lang_analysis.get('language_count', 0)
            }
        }

cv_analyzer = AdvancedCVAnalyzer()

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
    cursor.execute('INSERT INTO users (id, email, password_hash, full_name, phone, location, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                   (user_id, data.email, password_hash, data.full_name, data.phone, data.location, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return {"access_token": create_token(user_id), "user_id": user_id, "name": data.full_name}

@app.post("/api/auth/login")
async def login(data: LoginRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name, password_hash FROM users WHERE email = ?", (data.email,))
    user = cursor.fetchone()
    if user and verify_password(data.password, user[2]):
        conn.close()
        return {"access_token": create_token(user[0]), "user_id": user[0], "name": user[1]}
    conn.close()
    raise HTTPException(status_code=401, detail="Invalid credentials")

# ============ PROFILE UPDATE ============
@app.post("/api/user/update-profile")
async def update_user_profile(profile: dict, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    
    skills_str = ','.join(profile.get('skills', []))
    experience_data = json.dumps(profile.get('experience_data', []))
    education_data = json.dumps(profile.get('education_data', []))
    certification_data = json.dumps(profile.get('certification_data', []))
    achievement_data = json.dumps(profile.get('achievement_data', []))
    language_data = json.dumps(profile.get('language_data', []))
    
    cursor.execute('''
        UPDATE users SET 
            full_name = COALESCE(?, full_name),
            email = COALESCE(?, email),
            phone = COALESCE(?, phone),
            location = COALESCE(?, location),
            title = COALESCE(?, title),
            professional_summary = COALESCE(?, professional_summary),
            industry_sector = COALESCE(?, industry_sector),
            specialization_area = COALESCE(?, specialization_area),
            skills = ?,
            experience_years = COALESCE(?, experience_years),
            expected_salary = COALESCE(?, expected_salary),
            employment_type = COALESCE(?, employment_type),
            willing_to_relocate = COALESCE(?, willing_to_relocate),
            notice_period = COALESCE(?, notice_period),
            linkedin_url = COALESCE(?, linkedin_url),
            github_url = COALESCE(?, github_url),
            portfolio_url = COALESCE(?, portfolio_url),
            experience_data = ?,
            education_data = ?,
            certification_data = ?,
            achievement_data = ?,
            language_data = ?,
            volunteer_work = COALESCE(?, volunteer_work),
            publications = COALESCE(?, publications),
            memberships = COALESCE(?, memberships)
        WHERE id = ?
    ''', (
        profile.get('full_name'), profile.get('email'), profile.get('phone'),
        profile.get('location'), profile.get('title'), profile.get('professional_summary'),
        profile.get('industry_sector'), profile.get('specialization_area'),
        skills_str, profile.get('total_experience'), profile.get('expected_salary'),
        profile.get('employment_type'), profile.get('willing_to_relocate'),
        profile.get('notice_period'), profile.get('linkedin_url'), profile.get('github_url'),
        profile.get('portfolio_url'), experience_data, education_data, certification_data,
        achievement_data, language_data, profile.get('volunteer_work'), profile.get('publications'),
        profile.get('memberships'), current_user["user_id"]
    ))
    
    conn.commit()
    conn.close()
    return {"message": "Profile updated", "skills_count": len(profile.get('skills', []))}

@app.get("/api/user/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (current_user["user_id"],))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return {"skills": [], "experience_years": 0}
    
    return {
        "full_name": user['full_name'] or "",
        "email": user['email'] or "",
        "phone": user['phone'] or "",
        "location": user['location'] or "",
        "title": user['title'] or "",
        "professional_summary": user['professional_summary'] or "",
        "industry_sector": user['industry_sector'] or "",
        "specialization_area": user['specialization_area'] or "",
        "skills": user['skills'].split(',') if user['skills'] else [],
        "experience_years": user['experience_years'] or 0,
        "expected_salary": user['expected_salary'] or 0,
        "employment_type": user['employment_type'] or "",
        "willing_to_relocate": user['willing_to_relocate'] or "",
        "notice_period": user['notice_period'] or 0,
        "experience_data": json.loads(user['experience_data']) if user['experience_data'] else [],
        "education_data": json.loads(user['education_data']) if user['education_data'] else [],
        "certification_data": json.loads(user['certification_data']) if user['certification_data'] else [],
        "achievement_data": json.loads(user['achievement_data']) if user['achievement_data'] else [],
        "language_data": json.loads(user['language_data']) if user['language_data'] else [],
        "volunteer_work": user['volunteer_work'] or "",
        "publications": user['publications'] or "",
        "memberships": user['memberships'] or "",
        "linkedin_url": user['linkedin_url'] or "",
        "github_url": user['github_url'] or "",
        "portfolio_url": user['portfolio_url'] or ""
    }

# ============ JOB RECOMMENDATIONS ============
@app.get("/api/user/recommendations")
async def get_recommendations(current_user: dict = Depends(get_current_user), limit: int = 20):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (current_user["user_id"],))
    user_row = cursor.fetchone()
    
    if not user_row:
        conn.close()
        return {"user": {}, "recommendations": []}
    
    candidate = {
        "skills": user_row['skills'].split(',') if user_row['skills'] else [],
        "experience_years": user_row['experience_years'] or 0,
        "education_data": json.loads(user_row['education_data']) if user_row['education_data'] else [],
        "certification_data": json.loads(user_row['certification_data']) if user_row['certification_data'] else [],
        "achievement_data": json.loads(user_row['achievement_data']) if user_row['achievement_data'] else [],
        "language_data": json.loads(user_row['language_data']) if user_row['language_data'] else [],
        "industry_sector": user_row['industry_sector'] or "",
        "specialization_area": user_row['specialization_area'] or "",
        "location": user_row['location'] or "",
        "expected_salary": user_row['expected_salary'] or 0,
        "employment_type": user_row['employment_type'] or "",
        "willing_to_relocate": user_row['willing_to_relocate'] or "",
        "notice_period": user_row['notice_period'] or 0,
        "professional_summary": user_row['professional_summary'] or "",
        "volunteer_work": user_row['volunteer_work'] or "",
        "publications": user_row['publications'] or "",
        "memberships": user_row['memberships'] or "",
        "title": user_row['title'] or "",
        "full_name": user_row['full_name'] or "",
        "phone": user_row['phone'] or ""
    }
    
    cursor.execute('SELECT * FROM jobs WHERE status = "active"')
    jobs = cursor.fetchall()
    conn.close()
    
    recommendations = []
    for job in jobs:
        job_data = {
            "job_id": job['id'],
            "job_title": job['title'],
            "company": job['company_name'],
            "location": job['location'] or "Remote",
            "required_skills": job['required_skills'] or "",
            "salary_range": job['salary_range'] or "Negotiable",
            "experience_required": job['experience_required'] or 2,
            "industry_sector": job['industry_sector'] or "",
            "specialization_area": job['specialization_area'] or "",
            "required_education": job['required_education'] or "",
            "required_certifications": job['required_certifications'] or "",
            "employment_type": job['employment_type'] or "Full-time",
            "required_languages": job['required_languages'] or "",
            "required_software": job['required_software'] or "",
            "description": job['description'] or "",
            "title": job['title']
        }
        
        match_result = cv_analyzer.calculate_comprehensive_score(candidate, job_data)
        
        recommendations.append({
            "job_id": job_data["job_id"],
            "job_title": job_data["job_title"],
            "company": job_data["company"],
            "location": job_data["location"],
            "salary_range": job_data["salary_range"],
            "experience_required": job_data["experience_required"],
            "required_skills": job_data["required_skills"],
            "match_score": match_result["match_score"],
            "category": match_result["category"],
            "color": match_result["color"],
            "match_breakdown": match_result["breakdown"],
            "match_details": match_result["details"]
        })
    
    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    
    return {
        "user": {
            "skills": candidate["skills"],
            "experience_years": candidate["experience_years"],
            "industry": candidate["industry_sector"],
            "specialization": candidate["specialization_area"],
            "education_count": len(candidate["education_data"]),
            "certification_count": len(candidate["certification_data"]),
            "language_count": len(candidate["language_data"])
        },
        "recommendations": recommendations[:limit],
        "total_jobs": len(jobs)
    }

@app.post("/api/user/apply/{job_id}")
async def apply_for_job(job_id: str, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT full_name FROM users WHERE id = ?", (current_user["user_id"],))
    user = cursor.fetchone()
    cursor.execute("SELECT title, company_name FROM jobs WHERE id = ?", (job_id,))
    job = cursor.fetchone()
    
    if not job:
        conn.close()
        raise HTTPException(status_code=404, detail="Job not found")
    
    cursor.execute("SELECT id FROM applications WHERE user_id = ? AND job_id = ?", (current_user["user_id"], job_id))
    if cursor.fetchone():
        conn.close()
        return {"message": "Already applied"}
    
    app_id = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO applications (id, user_id, user_name, job_id, job_title, company_name, status, applied_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (app_id, current_user["user_id"], user[0], job_id, job[0], job[1], "pending", datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    return {"message": f"Applied for {job[0]}", "application_id": app_id}

@app.get("/api/user/applications")
async def get_applications(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, job_title, company_name, status, applied_at FROM applications WHERE user_id = ? ORDER BY applied_at DESC', (current_user["user_id"],))
    apps = cursor.fetchall()
    conn.close()
    return {"applications": [dict(app) for app in apps]}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "Ethiopian AI Job Match API Running"}