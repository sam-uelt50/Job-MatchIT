import pandas as pd
import random
from datetime import datetime

print("=" * 60)
print("CREATING ETHIOPIAN JOB DATASET")
print("=" * 60)

# Ethiopian companies
companies = [
    "Ethio Telecom", "Dashen Bank", "Ethiopian Airlines", "BGI Ethiopia", 
    "Habesha Brewery", "Mohamed International", "Sun Pharma Ethiopia",
    "East African Holding", "MIDROC Ethiopia", "Anbessa City Bus",
    "Ethiopian Electric Utility", "Addis Ababa University", "Black Lion Hospital",
    "St. Paul Hospital", "Unity University", "Ethiopian Construction Works",
    "Metal Engineering Corporation", "Ethiopian Roads Authority", "Commercial Bank of Ethiopia",
    "Ethio Lease", "Belayab Motors", "Kality Metal Factory", "Ayat Real Estate"
]

# Ethiopian cities
locations = ["Addis Ababa", "Bahir Dar", "Gondar", "Mekelle", "Hawassa", "Jimma", "Dire Dawa", "Adama", "Debre Birhan", "Arba Minch"]

# Job titles by industry
jobs_by_industry = {
    "Technology": [
        "Software Engineer", "Frontend Developer", "Backend Developer", 
        "Full Stack Developer", "Data Scientist", "IT Manager", 
        "Network Administrator", "Cybersecurity Analyst", "Database Administrator",
        "DevOps Engineer", "Mobile Developer", "UI/UX Designer", "Cloud Engineer"
    ],
    "Healthcare": [
        "Medical Doctor", "Registered Nurse", "Pharmacist", "Lab Technician",
        "Radiologist", "Physiotherapist", "Dentist", "Public Health Officer",
        "Health Extension Worker", "Clinical Officer", "Midwife", "Optometrist"
    ],
    "Engineering": [
        "Civil Engineer", "Electrical Engineer", "Mechanical Engineer",
        "Chemical Engineer", "Industrial Engineer", "Architect",
        "Project Engineer", "Structural Engineer", "Water Resource Engineer",
        "Environmental Engineer", "Software Engineer", "Biomedical Engineer"
    ],
    "Finance": [
        "Accountant", "Financial Analyst", "Bank Teller", "Credit Analyst",
        "Auditor", "Tax Consultant", "Investment Advisor", "Insurance Agent",
        "Risk Manager", "Treasury Officer", "Loan Officer"
    ],
    "Education": [
        "Teacher", "Professor", "School Principal", "Curriculum Developer",
        "Education Specialist", "Librarian", "Research Assistant", "Lecturer",
        "Academic Advisor", "Dean of Students"
    ],
    "Business": [
        "Marketing Manager", "Sales Representative", "HR Manager",
        "Business Analyst", "Project Manager", "Operations Manager",
        "Supply Chain Coordinator", "Customer Service Representative",
        "Administrative Assistant", "Office Manager", "Logistics Coordinator"
    ]
}

# Skills by job category
skills_map = {
    "Software Engineer": "Python,Java,JavaScript,SQL,Git,Problem Solving,Teamwork",
    "Frontend Developer": "React,HTML,CSS,JavaScript,TypeScript,UI/UX,Figma",
    "Backend Developer": "Python,Django,Node.js,SQL,REST APIs,API Development",
    "Data Scientist": "Python,Machine Learning,SQL,Statistics,TensorFlow,Pandas,Data Visualization",
    "Registered Nurse": "Patient Care,EMR,Vital Signs,Medication Admin,Communication,Teamwork",
    "Medical Doctor": "Diagnosis,Patient Care,Surgery,Prescription,Leadership,Empathy",
    "Civil Engineer": "AutoCAD,Structural Design,Project Management,Site Supervision,Mathematics",
    "Electrical Engineer": "Power Systems,Control Systems,Circuit Design,PLC,Electronics,Troubleshooting",
    "Accountant": "QuickBooks,Excel,Tax Preparation,Financial Analysis,Attention to Detail",
    "Teacher": "Lesson Planning,Classroom Management,Curriculum Development,Patience,Communication",
    "Marketing Manager": "Digital Marketing,SEO,Social Media,Content Strategy,Analytics,Creativity",
    "HR Manager": "Recruitment,Employee Relations,Performance Management,HR Policies,Interpersonal Skills",
    "Project Manager": "Agile,Scrum,Leadership,Risk Management,Budgeting,Scheduling",
    "DevOps Engineer": "AWS,Docker,Kubernetes,CI/CD,Linux,Automation,Git",
    "Network Administrator": "Cisco,Firewalls,Routing,Switching,TCP/IP,Network Security",
    "Cybersecurity Analyst": "Security Auditing,Risk Assessment,Penetration Testing,Firewalls,Encryption"
}

# Generate 300+ sample jobs
ethiopian_jobs = []
industries = list(jobs_by_industry.keys())

print("\n📊 Generating Ethiopian job dataset...")

for i in range(300):  # Generate 300 jobs
    industry = random.choice(industries)
    job_title = random.choice(jobs_by_industry[industry])
    company = random.choice(companies)
    location = random.choice(locations)
    experience_req = random.choice([0, 1, 2, 3, 4, 5, 6, 8, 10])
    
    # Get skills for this job title
    skills = skills_map.get(job_title, "Communication,Teamwork,Problem Solving")
    
    # Add some random extra skills
    extra_skills = ["Leadership", "Project Management", "Critical Thinking", "Time Management", "Adaptability"]
    if random.random() > 0.6:
        skills += "," + random.choice(extra_skills)
    
    salary_min = random.randint(25000, 80000)
    salary_max = salary_min + random.randint(15000, 80000)
    salary_range = f"{salary_min:,} - {salary_max:,} ETB"
    
    employment_types = ["Full-time", "Contract", "Remote", "Hybrid", "Part-time"]
    employment_type = random.choice(employment_types)
    
    ethiopian_jobs.append({
        "job_id": i + 1,
        "title": job_title,
        "company": company,
        "location": location,
        "industry": industry,
        "required_skills": skills,
        "experience_required": experience_req,
        "salary_range": salary_range,
        "employment_type": employment_type,
        "description": f"We are seeking a talented {job_title} to join our team in {location}. The ideal candidate has {experience_req}+ years of experience in the {industry} industry, strong {skills.split(',')[0]} skills, and a passion for excellence.",
        "posted_date": datetime.now().isoformat(),
        "status": "active"
    })
    print(f"   Added: {job_title} at {company} ({location})")

# Create DataFrame
df = pd.DataFrame(ethiopian_jobs)

# Save to CSV
df.to_csv('ethiopian_jobs_dataset.csv', index=False)

print(f"\n✅ SUCCESS! Created {len(df)} Ethiopian job records")
print(f"📁 File saved: ethiopian_jobs_dataset.csv")
print("\n📊 DATASET SUMMARY:")
print(f"   - Industries: {len(industries)}")
print(f"   - Companies: {len(companies)}")
print(f"   - Locations: {len(locations)}")
print(f"   - Unique Job Titles: {len(set(jobs_by_industry[industry] for industry in industries))}")
print("\n✅ Dataset ready for loading!")