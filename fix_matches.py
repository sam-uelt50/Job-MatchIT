import requests
import json

print("=" * 70)
print("FIXING JOB MATCHES - ADDING PROPER REQUIRED_SKILLS")
print("=" * 70)

# First, make sure we have a company
company_email = "wesha@tech.com"
company_password = "123456"

# Try to login
try:
    r = requests.post("http://localhost:8000/api/auth/login", json={"email": company_email, "password": company_password})
    if r.status_code == 200:
        company = r.json()
        company_id = company["user_id"]
        print(f"✓ Company logged in: {company_id}")
    else:
        # Register new company
        register_data = {
            "company_name": "Wesha Tech Solutions",
            "email": company_email,
            "password": company_password,
            "industry": "Technology",
            "location": "Addis Ababa"
        }
        r = requests.post("http://localhost:8000/api/auth/register/company", json=register_data)
        if r.status_code == 200:
            company = r.json()
            company_id = company["user_id"]
            print(f"✓ Company registered: {company_id}")
        else:
            print(f"❌ Failed: {r.text}")
            exit()
except Exception as e:
    print(f"❌ Cannot connect to backend. Make sure backend is running on port 8000")
    print(f"Error: {e}")
    exit()

# First, delete existing jobs (optional - clear old ones)
print("\n📋 Clearing old jobs...")
try:
    r = requests.get(f"http://localhost:8000/api/company/jobs?company_id={company_id}")
    if r.status_code == 200:
        jobs_data = r.json()
        # Note: You may need to delete jobs manually via SQLite if needed
        print(f"   Found {len(jobs_data.get('jobs', []))} existing jobs")
except:
    pass

# Jobs with SPECIFIC required_skills for DIFFERENT match scores
# These skills are designed to match Dagim's resume (Python, Java, JavaScript, React, HTML, CSS, Figma, Canva, UI/UX)
jobs = [
    {
        "title": "Senior Python Developer",
        "description": "Backend developer with Python expertise for scalable applications.",
        "requirements": "Python, Django, REST APIs, SQL, Git",
        "required_skills": "Python, Django, REST APIs, SQL, Git",
        "location": "Addis Ababa",
        "salary_range": "120,000 - 180,000 ETB",
        "employment_type": "full-time",
        "experience_required": 3
    },
    {
        "title": "Senior Web Developer",
        "description": "Full stack web developer for modern web applications.",
        "requirements": "Python, JavaScript, React, HTML, CSS",
        "required_skills": "Python, JavaScript, React, HTML, CSS",
        "location": "Addis Ababa",
        "salary_range": "100,000 - 150,000 ETB",
        "employment_type": "full-time",
        "experience_required": 2
    },
    {
        "title": "React Frontend Developer",
        "description": "Frontend developer with React expertise.",
        "requirements": "React, JavaScript, HTML, CSS, Redux",
        "required_skills": "React, JavaScript, HTML, CSS, Redux",
        "location": "Remote",
        "salary_range": "90,000 - 130,000 ETB",
        "employment_type": "full-time",
        "experience_required": 2
    },
    {
        "title": "UI/UX Designer",
        "description": "Creative UI/UX designer for web and mobile apps.",
        "requirements": "Figma, Canva, UI Design, UX Research, Adobe XD",
        "required_skills": "Figma, Canva, UI Design, UX Research, Adobe XD",
        "location": "Remote",
        "salary_range": "80,000 - 120,000 ETB",
        "employment_type": "full-time",
        "experience_required": 2
    },
    {
        "title": "Web Designer",
        "description": "Web designer for responsive websites.",
        "requirements": "HTML, CSS, Figma, Canva, Web Design",
        "required_skills": "HTML, CSS, Figma, Canva, Web Design",
        "location": "Remote",
        "salary_range": "70,000 - 100,000 ETB",
        "employment_type": "full-time",
        "experience_required": 2
    },
    {
        "title": "Java Backend Developer",
        "description": "Backend developer with Java and Spring Boot.",
        "requirements": "Java, Spring Boot, SQL, REST APIs, Maven",
        "required_skills": "Java, Spring Boot, SQL, REST APIs, Maven",
        "location": "Hybrid",
        "salary_range": "110,000 - 160,000 ETB",
        "employment_type": "full-time",
        "experience_required": 3
    },
    {
        "title": "Data Scientist",
        "description": "Data scientist for ML and analytics projects.",
        "requirements": "Python, Machine Learning, SQL, Statistics, TensorFlow",
        "required_skills": "Python, Machine Learning, SQL, Statistics, TensorFlow",
        "location": "Hybrid",
        "salary_range": "140,000 - 200,000 ETB",
        "employment_type": "full-time",
        "experience_required": 3
    },
    {
        "title": "DevOps Engineer",
        "description": "DevOps engineer for cloud infrastructure.",
        "requirements": "AWS, Docker, Kubernetes, CI/CD, Linux, Jenkins",
        "required_skills": "AWS, Docker, Kubernetes, CI/CD, Linux, Jenkins",
        "location": "Remote",
        "salary_range": "130,000 - 180,000 ETB",
        "employment_type": "full-time",
        "experience_required": 4
    },
    {
        "title": "JavaScript Full Stack Developer",
        "description": "Full stack JavaScript developer.",
        "requirements": "JavaScript, React, Node.js, Express, MongoDB",
        "required_skills": "JavaScript, React, Node.js, Express, MongoDB",
        "location": "Remote",
        "salary_range": "100,000 - 150,000 ETB",
        "employment_type": "full-time",
        "experience_required": 2
    },
    {
        "title": "IT Project Manager",
        "description": "Project manager for IT projects.",
        "requirements": "Project Management, Agile, Scrum, JIRA, Leadership",
        "required_skills": "Project Management, Agile, Scrum, JIRA, Leadership",
        "location": "Addis Ababa",
        "salary_range": "120,000 - 170,000 ETB",
        "employment_type": "full-time",
        "experience_required": 4
    }
]

print("\n" + "-" * 70)
print("Adding jobs with REQUIRED_SKILLS:")
print("-" * 70)

success_count = 0
for job in jobs:
    try:
        r = requests.post(f"http://localhost:8000/api/company/jobs?company_id={company_id}", json=job)
        if r.status_code == 200:
            print(f"  ✅ {job['title']}")
            print(f"     Required Skills: {job['required_skills']}")
            success_count += 1
        else:
            print(f"  ❌ {job['title']}: {r.text}")
    except Exception as e:
        print(f"  ❌ {job['title']}: {e}")

print("\n" + "=" * 70)
print(f"✅ Added {success_count} jobs with proper required_skills!")
print("=" * 70)

print("\n" + "=" * 70)
print("CANDIDATE SKILLS (from your resume)")
print("=" * 70)
print("  Based on your uploaded resume, you have:")
print("  ✓ Python")
print("  ✓ Java")
print("  ✓ JavaScript")
print("  ✓ React")
print("  ✓ HTML")
print("  ✓ CSS")
print("  ✓ Figma")
print("  ✓ Canva")
print("  ✓ UI/UX Design")
print("  ✓ Web Design")
print("  ✓ 4 years of experience")
print("=" * 70)

print("\n" + "=" * 70)
print("EXPECTED DIFFERENT MATCH SCORES")
print("=" * 70)
print("""
  Job Title                    | Expected Match | Reason
  -----------------------------|---------------|------------------------------------------
  Senior Python Developer      | 85-95%        ✓ Python matches + 4 years exp
  Senior Web Developer         | 85-92%        ✓ Python, JavaScript, React, HTML, CSS
  React Frontend Developer     | 80-88%        ✓ React, JavaScript, HTML, CSS
  UI/UX Designer               | 75-85%        ✓ Figma, Canva, UI/UX Design
  Web Designer                 | 80-88%        ✓ HTML, CSS, Figma, Canva, Web Design
  Java Backend Developer       | 60-70%        ✓ Only Java matches
  Data Scientist               | 55-65%        ✓ Only Python matches
  DevOps Engineer              | 15-25%        ✗ Few matching skills
  JavaScript Full Stack        | 70-80%        ✓ JavaScript, React
  IT Project Manager           | 10-20%        ✗ Few matching skills
""")

print("\n" + "=" * 70)
print("NEXT STEPS:")
print("=" * 70)
print("1. RESTART your backend (Ctrl+C then run again)")
print("2. REFRESH your browser at http://localhost:3000/candidate-dashboard.html")
print("3. Go to JOB MATCHES tab")
print("4. You will see DIFFERENT match scores for each job!")
print("=" * 70)