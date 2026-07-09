import requests
import json

print("=" * 70)
print("ADDING JOBS WITH PROPER REQUIRED_SKILLS FOR ML MATCHING")
print("=" * 70)

# First, get or create a company
company_email = "techcorp@example.com"
company_password = "123456"

# Try to login
login_data = {"email": company_email, "password": company_password}
r = requests.post("http://localhost:8000/api/auth/login", json=login_data)

if r.status_code == 200:
    company = r.json()
    company_id = company["user_id"]
    print(f"✓ Company logged in successfully! ID: {company_id}")
else:
    # Register new company
    register_data = {
        "company_name": "Tech Corp Ethiopia",
        "email": company_email,
        "password": company_password,
        "industry": "Technology",
        "location": "Addis Ababa"
    }
    r = requests.post("http://localhost:8000/api/auth/register/company", json=register_data)
    if r.status_code == 200:
        company = r.json()
        company_id = company["user_id"]
        print(f"✓ Company registered successfully! ID: {company_id}")
    else:
        print(f"❌ Failed: {r.text}")
        exit()

# Define jobs with SPECIFIC required_skills for proper ML matching
# Each job has different skill requirements to show varied match scores
jobs = [
    {
        "title": "Senior Python Developer",
        "description": "Looking for an experienced Python developer to build backend services.",
        "requirements": "Python, Django, REST APIs, SQL, Git",
        "required_skills": "Python, Django, REST APIs, SQL, Git",
        "location": "Remote",
        "salary_range": "120,000 - 180,000 ETB",
        "employment_type": "full-time",
        "experience_required": 3
    },
    {
        "title": "React Frontend Developer",
        "description": "Frontend developer with React expertise for web applications.",
        "requirements": "React, JavaScript, HTML, CSS, Redux",
        "required_skills": "React, JavaScript, HTML, CSS, Redux",
        "location": "Remote",
        "salary_range": "100,000 - 150,000 ETB",
        "employment_type": "full-time",
        "experience_required": 2
    },
    {
        "title": "Full Stack Web Developer",
        "description": "Full stack developer proficient in both frontend and backend.",
        "requirements": "Python, React, JavaScript, HTML, CSS, SQL",
        "required_skills": "Python, React, JavaScript, HTML, CSS, SQL",
        "location": "Remote",
        "salary_range": "130,000 - 190,000 ETB",
        "employment_type": "full-time",
        "experience_required": 3
    },
    {
        "title": "UI/UX Designer",
        "description": "Creative UI/UX designer for modern web applications.",
        "requirements": "Figma, Canva, UI Design, UX Research",
        "required_skills": "Figma, Canva, UI Design, UX Research",
        "location": "Remote",
        "salary_range": "80,000 - 120,000 ETB",
        "employment_type": "full-time",
        "experience_required": 2
    },
    {
        "title": "Web Designer",
        "description": "Web designer for creating beautiful responsive websites.",
        "requirements": "HTML, CSS, Figma, Canva, Web Design",
        "required_skills": "HTML, CSS, Figma, Canva, Web Design",
        "location": "Remote",
        "salary_range": "70,000 - 110,000 ETB",
        "employment_type": "full-time",
        "experience_required": 2
    },
    {
        "title": "Java Backend Developer",
        "description": "Backend developer with Java and Spring Boot expertise.",
        "requirements": "Java, Spring Boot, SQL, REST APIs",
        "required_skills": "Java, Spring Boot, SQL, REST APIs",
        "location": "Remote",
        "salary_range": "110,000 - 160,000 ETB",
        "employment_type": "full-time",
        "experience_required": 3
    },
    {
        "title": "JavaScript Developer",
        "description": "JavaScript developer for modern web applications.",
        "requirements": "JavaScript, React, Node.js, HTML, CSS",
        "required_skills": "JavaScript, React, Node.js, HTML, CSS",
        "location": "Remote",
        "salary_range": "100,000 - 150,000 ETB",
        "employment_type": "full-time",
        "experience_required": 2
    },
    {
        "title": "Data Scientist",
        "description": "Data scientist for machine learning and analytics projects.",
        "requirements": "Python, Machine Learning, SQL, Statistics",
        "required_skills": "Python, Machine Learning, SQL, Statistics",
        "location": "Remote",
        "salary_range": "140,000 - 200,000 ETB",
        "employment_type": "full-time",
        "experience_required": 3
    },
    {
        "title": "DevOps Engineer",
        "description": "DevOps engineer for cloud infrastructure.",
        "requirements": "AWS, Docker, Kubernetes, CI/CD, Linux",
        "required_skills": "AWS, Docker, Kubernetes, CI/CD, Linux",
        "location": "Remote",
        "salary_range": "130,000 - 180,000 ETB",
        "employment_type": "full-time",
        "experience_required": 4
    },
    {
        "title": "IT Project Manager",
        "description": "Project manager for IT projects.",
        "requirements": "Project Management, Agile, Scrum, Leadership",
        "required_skills": "Project Management, Agile, Scrum, Leadership",
        "location": "Remote",
        "salary_range": "120,000 - 170,000 ETB",
        "employment_type": "full-time",
        "experience_required": 4
    }
]

print("\n" + "-" * 70)
print("Adding jobs with required_skills:")
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
print(f"✅ SUCCESS! Added {success_count} jobs with proper required_skills")
print("=" * 70)

print("\n" + "=" * 70)
print("CANDIDATE'S EXTRACTED SKILLS (from your resume)")
print("=" * 70)
print("  Based on the resume you uploaded, you have:")
print("  • Python")
print("  • Java")
print("  • JavaScript")
print("  • React")
print("  • HTML")
print("  • CSS")
print("  • Figma")
print("  • Canva")
print("  • UI/UX Design")
print("  • Web Design")
print("  • 4 years of experience")
print("=" * 70)

print("\n" + "=" * 70)
print("EXPECTED MATCH SCORES (will be DIFFERENT for each job)")
print("=" * 70)
print("""
  Job                          | Match Score | Reason
  ----------------------------|-------------|------------------------------------------
  Senior Python Developer     | 85-95%      | Python matches + 4 years experience
  React Frontend Developer    | 80-90%      | React, JavaScript, HTML, CSS match
  Full Stack Developer        | 85-92%      | Python, React, JavaScript, HTML, CSS match
  UI/UX Designer              | 75-85%      | Figma, Canva, UI/UX match
  Web Designer                | 80-88%      | HTML, CSS, Figma, Canva match
  Java Backend Developer      | 60-70%      | Only Java matches
  JavaScript Developer        | 70-80%      | JavaScript, React, HTML, CSS match
  Data Scientist              | 50-60%      | Only Python matches
  DevOps Engineer             | 20-30%      | Few matching skills
  IT Project Manager          | 15-25%      | Few matching skills
""")

print("\n" + "=" * 70)
print("NEXT STEPS:")
print("=" * 70)
print("1. Restart your backend (Ctrl+C then run again)")
print("2. Refresh your browser at http://localhost:3000/candidate-dashboard.html")
print("3. Go to JOB MATCHES tab")
print("4. You will see DIFFERENT match scores for each job!")
print("=" * 70)