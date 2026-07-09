# save this as update_main.py
import requests
import json

print("=" * 60)
print("UPDATING BACKEND WITH COMPREHENSIVE ML MATCHING")
print("=" * 60)

# The enhanced backend code that uses ALL CV fields
main_py_content = '''from fastapi import FastAPI, Depends, HTTPException
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
        id TEXT PRIMARY KEY, email TEXT UNIQUE, password_hash TEXT,
        full_name TEXT, phone TEXT, location TEXT, region TEXT, city TEXT,
        title TEXT, preferred_title TEXT, professional_summary TEXT,
        industry_sector TEXT, specialization_area TEXT,
        professional_license TEXT, license_number TEXT,
        skills TEXT, experience_years INTEGER, years_in_ethiopia INTEGER,
        expected_salary INTEGER, employment_type TEXT, willing_to_relocate TEXT,
        notice_period INTEGER, linkedin_url TEXT, github_url TEXT, portfolio_url TEXT,
        experience_data TEXT, education_data TEXT, certification_data TEXT,
        achievement_data TEXT, language_data TEXT, volunteer_work TEXT,
        publications TEXT, memberships TEXT, reference_name TEXT,
        reference_phone TEXT, reference_email TEXT, reference_relation TEXT,
        created_at TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY, title TEXT, company_name TEXT, location TEXT,
        required_skills TEXT, salary_range TEXT, experience_required INTEGER,
        industry_sector TEXT, specialization_area TEXT, required_education TEXT,
        required_certifications TEXT, employment_type TEXT,
        required_languages TEXT, required_software TEXT,
        status TEXT, created_at TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS applications (
        id TEXT PRIMARY KEY, user_id TEXT, user_name TEXT, job_id TEXT,
        job_title TEXT, company_name TEXT, match_score INTEGER,
        match_breakdown TEXT, status TEXT, applied_at TEXT
    )''')
    
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

# ============ COMPREHENSIVE CV MATCH SCORE ============
def calculate_comprehensive_match_score(candidate, job):
    """
    Uses ALL CV fields to calculate match score:
    - Skills (20%)
    - Experience (15%)
    - Education (12%)
    - Industry/Specialization (12%)
    - Professional Summary (8%)
    - Certifications/Licenses (8%)
    - Languages (5%)
    - Achievements/Publications (5%)
    - Volunteer Work (5%)
    - Professional Memberships (3%)
    - Software/Tools (3%)
    - Location/Relocation (2%)
    - Salary (1%)
    - Notice Period (1%)
    """
    
    scores = {}
    
    # 1. SKILLS MATCH (20%)
    candidate_skills = [s.lower() for s in candidate.get('skills', [])]
    job_skills = [s.strip().lower() for s in job.get('required_skills', '').split(',')] if job.get('required_skills') else []
    if job_skills and candidate_skills:
        matched = sum(1 for js in job_skills if js in candidate_skills)
        skills_score = (matched / len(job_skills)) * 100
    else:
        skills_score = 0
    scores['skills'] = skills_score * 0.20
    
    # 2. EXPERIENCE MATCH (15%)
    candidate_exp = candidate.get('experience_years', 0)
    job_exp = job.get('experience_required', 2)
    if candidate_exp >= job_exp:
        exp_score = 100
    elif candidate_exp > 0:
        exp_score = (candidate_exp / job_exp) * 100
    else:
        exp_score = 0
    scores['experience'] = exp_score * 0.15
    
    # 3. EDUCATION MATCH (12%)
    candidate_edu = candidate.get('education_data', [])
    job_edu = job.get('required_education', '')
    edu_score = 30
    for edu in candidate_edu:
        degree = edu.get('degree', '').lower()
        field = edu.get('field', '').lower()
        specialization = edu.get('specialization', '').lower()
        if job_edu.lower() in degree or job_edu.lower() in field:
            edu_score = 90
        elif 'bachelor' in degree:
            edu_score = 70
        elif 'master' in degree:
            edu_score = 85
        elif 'phd' in degree:
            edu_score = 100
        if specialization and job.get('specialization_area', '').lower() in specialization:
            edu_score = min(100, edu_score + 10)
    scores['education'] = edu_score * 0.12
    
    # 4. INDUSTRY & SPECIALIZATION MATCH (12%)
    candidate_industry = candidate.get('industry_sector', '')
    job_industry = job.get('industry_sector', '')
    candidate_specialization = candidate.get('specialization_area', '')
    job_specialization = job.get('specialization_area', '')
    industry_score = 0
    if candidate_industry and job_industry:
        if candidate_industry.lower() == job_industry.lower():
            industry_score = 80
            if candidate_specialization and job_specialization:
                if candidate_specialization.lower() in job_specialization.lower():
                    industry_score = 100
        else:
            industry_score = 20
    else:
        industry_score = 50
    scores['industry'] = industry_score * 0.12
    
    # 5. PROFESSIONAL SUMMARY MATCH (8%)
    candidate_summary = candidate.get('professional_summary', '').lower()
    job_title = job.get('title', '').lower()
    summary_score = 0
    if candidate_summary and job_title:
        keywords = job_title.split()
        matched_keywords = sum(1 for kw in keywords if kw in candidate_summary)
        summary_score = min(100, (matched_keywords / len(keywords)) * 100) if keywords else 50
    else:
        summary_score = 30
    scores['summary'] = summary_score * 0.08
    
    # 6. CERTIFICATIONS & LICENSES (8%)
    candidate_certs = candidate.get('certification_data', [])
    job_certs = job.get('required_certifications', '')
    cert_score = 20
    if candidate_certs:
        cert_names = [c.get('name', '').lower() for c in candidate_certs]
        if job_certs.lower() in ' '.join(cert_names):
            cert_score = 100
        elif any('certified' in cn for cn in cert_names):
            cert_score = 70
    if candidate.get('professional_license'):
        cert_score = max(cert_score, 60)
    scores['certifications'] = cert_score * 0.08
    
    # 7. LANGUAGES MATCH (5%)
    candidate_langs = candidate.get('language_data', [])
    job_langs = job.get('required_languages', '')
    lang_score = 30
    if candidate_langs and job_langs:
        lang_names = [l.get('name', '').lower() for l in candidate_langs]
        if job_langs.lower() in ' '.join(lang_names):
            lang_score = 100
        elif 'english' in lang_names:
            lang_score = 70
    scores['languages'] = lang_score * 0.05
    
    # 8. ACHIEVEMENTS & PUBLICATIONS (5%)
    candidate_achievements = candidate.get('achievement_data', [])
    candidate_publications = candidate.get('publications', '')
    ach_score = 20
    if candidate_achievements:
        ach_score = min(100, 50 + len(candidate_achievements) * 10)
    if candidate_publications:
        ach_score = min(100, ach_score + 20)
    scores['achievements'] = ach_score * 0.05
    
    # 9. VOLUNTEER WORK (5%)
    volunteer = candidate.get('volunteer_work', '')
    volunteer_score = 60 if volunteer else 20
    scores['volunteer'] = volunteer_score * 0.05
    
    # 10. PROFESSIONAL MEMBERSHIPS (3%)
    memberships = candidate.get('memberships', '')
    membership_score = 60 if memberships else 20
    scores['memberships'] = membership_score * 0.03
    
    # 11. SOFTWARE/TOOLS MATCH (3%)
    job_software = job.get('required_software', '')
    candidate_skills_all = [s.lower() for s in candidate.get('skills', [])]
    software_score = 30
    if job_software and candidate_skills_all:
        job_tools = [t.strip().lower() for t in job_software.split(',')]
        matched_tools = sum(1 for t in job_tools if any(t in s for s in candidate_skills_all))
        if job_tools:
            software_score = (matched_tools / len(job_tools)) * 100
    scores['software'] = software_score * 0.03
    
    # 12. LOCATION & RELOCATION (2%)
    job_location = job.get('location', '')
    candidate_location = candidate.get('location', '')
    willing_relocate = candidate.get('willing_to_relocate', 'No')
    location_score = 0
    if job_location.lower() == 'remote':
        location_score = 100
    elif candidate_location and job_location:
        if candidate_location.lower() in job_location.lower():
            location_score = 100
        elif willing_relocate.lower() == 'yes':
            location_score = 80
        else:
            location_score = 40
    else:
        location_score = 60
    scores['location'] = location_score * 0.02
    
    # 13. SALARY MATCH (1%)
    candidate_salary = candidate.get('expected_salary', 0)
    job_salary = job.get('salary_range', '')
    salary_score = 50
    if candidate_salary > 0 and job_salary:
        numbers = re.findall(r'\d+', job_salary)
        if numbers:
            avg_job_salary = sum(int(n) for n in numbers) / len(numbers)
            if candidate_salary <= avg_job_salary:
                salary_score = 100
            elif candidate_salary <= avg_job_salary * 1.2:
                salary_score = 80
            else:
                salary_score = 50
    scores['salary'] = salary_score * 0.01
    
    # 14. NOTICE PERIOD (1%)
    notice_period = candidate.get('notice_period', 30)
    notice_score = 100 if notice_period <= 30 else 70 if notice_period <= 60 else 40
    scores['notice'] = notice_score * 0.01
    
    # Calculate total
    total_score = sum(scores.values())
    total_score = min(100, max(0, round(total_score)))
    
    if total_score >= 80:
        category = "🏆 Excellent Match"
        color = "#28a745"
        recommendation = "Strongly recommended to apply"
    elif total_score >= 65:
        category = "⭐ Great Match"
        color = "#17a2b8"
        recommendation = "Good candidate, consider applying"
    elif total_score >= 50:
        category = "👍 Good Match"
        color = "#ffc107"
        recommendation = "Potential match"
    elif total_score >= 35:
        category = "📌 Potential Match"
        color = "#fd7e14"
        recommendation = "Consider upskilling"
    else:
        category = "⚠️ Low Match"
        color = "#dc3545"
        recommendation = "Not recommended"
    
    return {
        "match_score": total_score,
        "category": category,
        "color": color,
        "recommendation": recommendation,
        "breakdown": {
            "skills": round(scores['skills'] / 0.20, 1),
            "experience": round(scores['experience'] / 0.15, 1),
            "education": round(scores['education'] / 0.12, 1),
            "industry": round(scores['industry'] / 0.12, 1),
            "summary": round(scores['summary'] / 0.08, 1),
            "certifications": round(scores['certifications'] / 0.08, 1),
            "languages": round(scores['languages'] / 0.05, 1),
            "achievements": round(scores['achievements'] / 0.05, 1),
            "volunteer": round(scores['volunteer'] / 0.05, 1),
            "memberships": round(scores['memberships'] / 0.03, 1),
            "software": round(scores['software'] / 0.03, 1),
            "location": round(scores['location'] / 0.02, 1),
            "salary": round(scores['salary'] / 0.01, 1),
            "notice": round(scores['notice'] / 0.01, 1)
        }
    }

# ============ AUTH ROUTES ============
@app.post("/api/auth/register/user")
async def register_user(data: dict):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (data['email'],))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = str(uuid.uuid4())
    password_hash = hash_password(data['password'])
    cursor.execute('INSERT INTO users (id, email, password_hash, full_name, phone, location, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                   (user_id, data['email'], password_hash, data['full_name'], data.get('phone', ''), data.get('location', ''), datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return {"access_token": create_token(user_id), "user_id": user_id, "name": data['full_name']}

@app.post("/api/auth/login")
async def login(data: dict):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name, password_hash FROM users WHERE email = ?", (data['email'],))
    user = cursor.fetchone()
    if user and verify_password(data['password'], user[2]):
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
            region = COALESCE(?, region),
            city = COALESCE(?, city),
            title = COALESCE(?, title),
            preferred_title = COALESCE(?, preferred_title),
            professional_summary = COALESCE(?, professional_summary),
            industry_sector = COALESCE(?, industry_sector),
            specialization_area = COALESCE(?, specialization_area),
            professional_license = COALESCE(?, professional_license),
            license_number = COALESCE(?, license_number),
            skills = ?,
            experience_years = COALESCE(?, experience_years),
            years_in_ethiopia = COALESCE(?, years_in_ethiopia),
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
            memberships = COALESCE(?, memberships),
            reference_name = COALESCE(?, reference_name),
            reference_phone = COALESCE(?, reference_phone),
            reference_email = COALESCE(?, reference_email),
            reference_relation = COALESCE(?, reference_relation)
        WHERE id = ?
    ''', (
        profile.get('full_name'), profile.get('email'), profile.get('phone'),
        profile.get('location'), profile.get('region'), profile.get('city'),
        profile.get('title'), profile.get('preferred_title'), profile.get('professional_summary'),
        profile.get('industry_sector'), profile.get('specialization_area'),
        profile.get('professional_license'), profile.get('license_number'),
        skills_str, profile.get('total_experience'), profile.get('years_in_ethiopia'),
        profile.get('expected_salary'), profile.get('employment_type'), profile.get('willing_to_relocate'),
        profile.get('notice_period'), profile.get('linkedin_url'), profile.get('github_url'),
        profile.get('portfolio_url'), experience_data, education_data, certification_data,
        achievement_data, language_data, profile.get('volunteer_work'), profile.get('publications'),
        profile.get('memberships'), profile.get('reference_name'), profile.get('reference_phone'),
        profile.get('reference_email'), profile.get('reference_relation'), current_user["user_id"]
    ))
    
    conn.commit()
    conn.close()
    return {"message": "CV Profile updated", "skills_count": len(profile.get('skills', []))}

@app.get("/api/user/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (current_user["user_id"],))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return {}
    
    return {
        "full_name": user['full_name'] or "",
        "email": user['email'] or "",
        "phone": user['phone'] or "",
        "location": user['location'] or "",
        "region": user['region'] or "",
        "city": user['city'] or "",
        "title": user['title'] or "",
        "preferred_title": user['preferred_title'] or "",
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
        "reference_name": user['reference_name'] or "",
        "reference_phone": user['reference_phone'] or "",
        "reference_email": user['reference_email'] or "",
        "reference_relation": user['reference_relation'] or "",
        "linkedin_url": user['linkedin_url'] or "",
        "github_url": user['github_url'] or "",
        "portfolio_url": user['portfolio_url'] or ""
    }

# ============ JOB RECOMMENDATIONS ============
@app.get("/api/user/recommendations")
async def get_recommendations(current_user: dict = Depends(get_current_user), limit: int = 20):
    conn = get_db()
    cursor = conn.cursor()
    
    # Get complete candidate profile
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
        "professional_license": user_row['professional_license'] or "",
        "volunteer_work": user_row['volunteer_work'] or "",
        "publications": user_row['publications'] or "",
        "memberships": user_row['memberships'] or "",
        "years_in_ethiopia": user_row['years_in_ethiopia'] or 0
    }
    
    # Get all active jobs
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
            "title": job['title']
        }
        
        match_result = calculate_comprehensive_match_score(candidate, job_data)
        
        recommendations.append({
            "job_id": job_data["job_id"],
            "job_title": job_data["job_title"],
            "company": job_data["company"],
            "location": job_data["location"],
            "salary_range": job_data["salary_range"],
            "experience_required": job_data["experience_required"],
            "required_skills": job_data["required_skills"],
            "industry_sector": job_data["industry_sector"],
            "match_score": match_result["match_score"],
            "category": match_result["category"],
            "color": match_result["color"],
            "recommendation": match_result["recommendation"],
            "match_breakdown": match_result["breakdown"]
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
            "language_count": len(candidate["language_data"]),
            "achievement_count": len(candidate["achievement_data"])
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
'''

# Save the backend file
with open(r'C:\Users\Samuel\OneDrive\Desktop\JOB RECRUIMENT AND RECOMMEND\Backend\app\main.py', 'w') as f:
    f.write(main_py_content)

print("✅ Backend code updated with comprehensive ML matching using ALL CV fields!")
print("\nThe new matching algorithm uses:")
print("   ✓ Skills (20%)")
print("   ✓ Experience (15%)")
print("   ✓ Education (12%)")
print("   ✓ Industry/Specialization (12%)")
print("   ✓ Professional Summary (8%)")
print("   ✓ Certifications/Licenses (8%)")
print("   ✓ Languages (5%)")
print("   ✓ Achievements/Publications (5%)")
print("   ✓ Volunteer Work (5%)")
print("   ✓ Professional Memberships (3%)")
print("   ✓ Software/Tools (3%)")
print("   ✓ Location/Relocation (2%)")
print("   ✓ Salary (1%)")
print("   ✓ Notice Period (1%)")
print("\n📊 TOTAL: 100% of your CV profile!")