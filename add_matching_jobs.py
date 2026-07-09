
import sqlite3
import uuid
from datetime import datetime

print("=" * 70)
print("ADDING JOBS WITH REQUIRED SKILLS FOR ML MATCHING")
print("=" * 70)

db_path = r'C:\Users\Samuel\OneDrive\Desktop\JOB RECRUIMENT AND RECOMMEND\Backend\job_recruitment.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# First, get or create a company ID
cursor.execute("SELECT id FROM companies LIMIT 1")
company = cursor.fetchone()

if company:
    company_id = company[0]
    print(f"✓ Found existing company: {company_id}")
else:
    # Create a default company
    company_id = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO companies (id, company_name, email, password_hash, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (company_id, 'Tech Corp Ethiopia', 'tech@jobmatch.com', 'dummy_hash', datetime.now().isoformat()))
    print(f"✓ Created new company: {company_id}")

# Clear old jobs
cursor.execute('DELETE FROM jobs')
print("✓ Cleared old jobs")

# Jobs with REQUIRED SKILLS that match YOUR profile
jobs = [
    ('React Frontend Developer', 'Innovate Solutions', 'Remote', 
     'React,JavaScript,HTML,CSS,Tailwind,Redux', 2, '100,000 - 150,000 ETB'),
    
    ('Full Stack Developer', 'WebWorks', 'Remote', 
     'Python,React,JavaScript,Node.js,MongoDB,FastAPI', 3, '130,000 - 190,000 ETB'),
    
    ('ML Engineer', 'AI Analytics', 'Remote', 
     'Python,Machine Learning,NLP,TensorFlow,API Development', 3, '150,000 - 220,000 ETB'),
    
    ('Senior Python Developer', 'Tech Corp', 'Remote', 
     'Python,Django,SQL,REST APIs,FastAPI,PostgreSQL', 3, '120,000 - 180,000 ETB'),
    
    ('Backend Developer', 'API Experts', 'Remote', 
     'Python,FastAPI,SQL,MongoDB,REST APIs,API Design', 3, '110,000 - 160,000 ETB'),
    
    ('JavaScript Developer', 'Web Agency', 'Remote', 
     'JavaScript,React,Node.js,Express,MongoDB', 2, '90,000 - 140,000 ETB'),
    
    ('Data Scientist', 'Data Corp', 'Remote', 
     'Python,Machine Learning,SQL,Statistics,Pandas', 3, '140,000 - 200,000 ETB'),
    
    ('UI/UX Designer', 'Creative Designs', 'Remote', 
     'Figma,Adobe XD,UI Design,UX Research,Prototyping', 2, '80,000 - 120,000 ETB'),
    
    ('Java Developer', 'Enterprise Solutions', 'Remote', 
     'Java,Spring Boot,SQL,REST APIs,Hibernate', 3, '100,000 - 150,000 ETB'),
    
    ('DevOps Engineer', 'Cloud Services', 'Remote', 
     'AWS,Docker,Kubernetes,CI/CD,Linux,Terraform', 4, '130,000 - 180,000 ETB')
]

for title, company_name, location, skills, exp, salary in jobs:
    job_id = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO jobs (id, company_id, company_name, title, location, required_skills, experience_required, salary_range, created_at, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (job_id, company_id, company_name, title, location, skills, exp, salary, datetime.now().isoformat(), 'active'))
    print(f"✓ Added: {title}")

conn.commit()
conn.close()

print(f"\n✅ Added {len(jobs)} jobs with different skill requirements")
print("\n" + "=" * 70)
print("EXPECTED MATCH SCORES (Based on YOUR skills)")
print("=" * 70)
print("""
┌─────────────────────────────┬──────────────────────────────────┬──────────┐
│ JOB TITLE                   │ WHY MATCH                        │ SCORE    │
├─────────────────────────────┼──────────────────────────────────┼──────────┤
│ React Frontend Developer    │ React, JS, HTML, CSS match       │ 90-95%   │
│ Full Stack Developer        │ Python, React, JS, Node.js match │ 85-90%   │
│ ML Engineer                 │ Python, ML, NLP, API match       │ 80-85%   │
│ Senior Python Developer     │ Python, SQL, FastAPI match       │ 75-80%   │
│ Backend Developer           │ Python, FastAPI, SQL match       │ 75-80%   │
│ JavaScript Developer        │ JS, React, Node.js match         │ 70-75%   │
│ Data Scientist              │ Python, ML, SQL match            │ 60-65%   │
│ UI/UX Designer              │ Figma (partial)                  │ 45-50%   │
│ Java Developer              │ Only Java matches                │ 40-45%   │
│ DevOps Engineer             │ Few matches                      │ 15-20%   │
└─────────────────────────────┴──────────────────────────────────┴──────────┘
""")
print("=" * 70)
print("✅ Now restart your backend and check Job Matches!")
print("=" * 70)