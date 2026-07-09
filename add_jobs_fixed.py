import requests
import json
import time

print("=" * 70)
print("ADDING JOBS WITH PROPER REQUIRED_SKILLS")
print("=" * 70)

# Step 1: Register a new company
company_data = {
    "company_name": "Tech Solutions Ethiopia",
    "email": "tech@ethiopia.com",
    "password": "admin123",
    "industry": "Technology",
    "location": "Addis Ababa"
}

print("\n[1/4] Registering company...")
r = requests.post("http://localhost:8000/api/auth/register/company", json=company_data)

if r.status_code == 200:
    company = r.json()
    access_token = company["access_token"]
    company_id = company["user_id"]
    print(f"✓ Company registered successfully!")
    print(f"  Token: {access_token[:50]}...")
    print(f"  Company ID: {company_id}")
else:
    # Try to login instead
    print("  Company may already exist, trying to login...")
    login_data = {
        "email": "tech@ethiopia.com",
        "password": "admin123"
    }
    r = requests.post("http://localhost:8000/api/auth/login", json=login_data)
    if r.status_code == 200:
        company = r.json()
        access_token = company["access_token"]
        company_id = company["user_id"]
        print(f"✓ Company logged in successfully!")
        print(f"  Token: {access_token[:50]}...")
    else:
        print(f"❌ Failed: {r.text}")
        print("\nMake sure backend is running on port 8000")
        exit()

# Jobs with specific required_skills
jobs = [
    {
        "title": "Senior Python Developer",
        "description": "Backend developer with Python expertise",
        "requirements": "Python, Django, REST APIs, SQL, Git",
        "required_skills": "Python, Django, REST APIs, SQL, Git",
        "location": "Remote",
        "salary_range": "120000-180000",
        "employment_type": "full-time",
        "experience_required": 3
    },
    {
        "title": "Senior Web Developer",
        "description": "Full stack web developer",
        "requirements": "Python, JavaScript, React, HTML, CSS",
        "required_skills": "Python, JavaScript, React, HTML, CSS",
        "location": "Remote",
        "salary_range": "100000-150000",
        "employment_type": "full-time",
        "experience_required": 2
    },
    {
        "title": "React Frontend Developer",
        "description": "Frontend developer with React",
        "requirements": "React, JavaScript, HTML, CSS, Redux",
        "required_skills": "React, JavaScript, HTML, CSS, Redux",
        "location": "Remote",
        "salary_range": "90000-130000",
        "employment_type": "full-time",
        "experience_required": 2
    },
    {
        "title": "UI/UX Designer",
        "description": "UI/UX designer for web and mobile",
        "requirements": "Figma, Canva, UI Design, UX Research",
        "required_skills": "Figma, Canva, UI Design, UX Research",
        "location": "Remote",
        "salary_range": "80000-120000",
        "employment_type": "full-time",
        "experience_required": 2
    },
    {
        "title": "Web Designer",
        "description": "Web designer for responsive websites",
        "requirements": "HTML, CSS, Figma, Canva, Web Design",
        "required_skills": "HTML, CSS, Figma, Canva, Web Design",
        "location": "Remote",
        "salary_range": "70000-100000",
        "employment_type": "full-time",
        "experience_required": 2
    },
    {
        "title": "Java Backend Developer",
        "description": "Backend developer with Java",
        "requirements": "Java, Spring Boot, SQL, REST APIs",
        "required_skills": "Java, Spring Boot, SQL, REST APIs",
        "location": "Hybrid",
        "salary_range": "110000-160000",
        "employment_type": "full-time",
        "experience_required": 3
    },
    {
        "title": "Data Scientist",
        "description": "Data scientist for ML projects",
        "requirements": "Python, Machine Learning, SQL, Statistics",
        "required_skills": "Python, Machine Learning, SQL, Statistics",
        "location": "Hybrid",
        "salary_range": "140000-200000",
        "employment_type": "full-time",
        "experience_required": 3
    },
    {
        "title": "DevOps Engineer",
        "description": "DevOps engineer for cloud",
        "requirements": "AWS, Docker, Kubernetes, CI/CD, Linux",
        "required_skills": "AWS, Docker, Kubernetes, CI/CD, Linux",
        "location": "Remote",
        "salary_range": "130000-180000",
        "employment_type": "full-time",
        "experience_required": 4
    },
    {
        "title": "JavaScript Developer",
        "description": "JavaScript full stack developer",
        "requirements": "JavaScript, React, Node.js, Express, MongoDB",
        "required_skills": "JavaScript, React, Node.js, Express, MongoDB",
        "location": "Remote",
        "salary_range": "100000-150000",
        "employment_type": "full-time",
        "experience_required": 2
    },
    {
        "title": "IT Project Manager",
        "description": "Project manager for IT",
        "requirements": "Project Management, Agile, Scrum, Leadership",
        "required_skills": "Project Management, Agile, Scrum, Leadership",
        "location": "Addis Ababa",
        "salary_range": "120000-170000",
        "employment_type": "full-time",
        "experience_required": 4
    }
]

print("\n[2/4] Adding jobs with required_skills...")
print("-" * 70)

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

success_count = 0
for job in jobs:
    try:
        r = requests.post(
            f"http://localhost:8000/api/company/jobs?company_id={company_id}",
            json=job,
            headers=headers
        )
        if r.status_code == 200:
            print(f"  ✅ {job['title']}")
            print(f"     Skills: {job['required_skills']}")
            success_count += 1
        else:
            print(f"  ❌ {job['title']}: {r.text}")
    except Exception as e:
        print(f"  ❌ {job['title']}: {e}")
    time.sleep(0.2)

print("\n[3/4] Verifying jobs were added...")
print("-" * 70)

# Check if jobs were added
try:
    r = requests.get(f"http://localhost:8000/api/company/jobs?company_id={company_id}", headers=headers)
    if r.status_code == 200:
        jobs_data = r.json()
        job_list = jobs_data.get("jobs", [])
        print(f"  Total jobs in database: {len(job_list)}")
        for job in job_list:
            print(f"    - {job.get('title')}: {job.get('required_skills', 'No skills')[:50]}...")
except Exception as e:
    print(f"  Could not verify: {e}")

print("\n" + "=" * 70)
print(f"[4/4] ✅ Added {success_count} jobs with proper required_skills!")
print("=" * 70)

print("\n" + "=" * 70)
print("CANDIDATE SKILLS NEEDED (from your resume)")
print("=" * 70)
print("""
  Based on your uploaded resume, you should have these skills:
  ✓ Python
  ✓ Java  
  ✓ JavaScript
  ✓ React
  ✓ HTML
  ✓ CSS
  ✓ Figma
  ✓ Canva
  ✓ UI/UX Design
  ✓ Web Design
  ✓ 4 years of experience
""")

print("\n" + "=" * 70)
print("EXPECTED MATCH SCORES (WILL BE DIFFERENT FOR EACH JOB)")
print("=" * 70)
print("""
  Job                         | Match Score | Color
  ----------------------------|-------------|--------
  Senior Python Developer     | 85-95%      | 🟢 Green
  Senior Web Developer        | 80-90%      | 🟢 Green  
  React Frontend Developer    | 75-85%      | 🔵 Blue
  UI/UX Designer              | 70-80%      | 🔵 Blue
  Web Designer                | 75-85%      | 🔵 Blue
  Java Backend Developer      | 55-65%      | 🟡 Yellow
  Data Scientist              | 50-60%      | 🟡 Yellow
  DevOps Engineer             | 15-25%      | 🔴 Red
  JavaScript Developer        | 65-75%      | 🟡 Yellow
  IT Project Manager          | 10-20%      | 🔴 Red
""")

print("\n" + "=" * 70)
print("NEXT STEPS:")
print("=" * 70)
print("""
1. RESTART your backend (Ctrl+C then run again):
   cd Backend
   python -m uvicorn app.main:app --reload --port 8000

2. Go to: http://localhost:3000/candidate-dashboard.html

3. LOGIN with any email/password

4. Go to "My Profile" and ADD YOUR SKILLS:
   - Type: Python, JavaScript, React, HTML, CSS, Figma, Canva, UI/UX
   - Press Enter after each skill
   - Set Experience: 4 years
   - Click SAVE

5. Go to "Job Matches" - You will see DIFFERENT scores!
""")
print("=" * 70)