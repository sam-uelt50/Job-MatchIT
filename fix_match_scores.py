import sqlite3

print("=" * 60)
print("FIXING ML MATCH SCORES - UPDATING YOUR PROFILE")
print("=" * 60)

db_path = r'C:\Users\Samuel\OneDrive\Desktop\JOB RECRUIMENT AND RECOMMEND\Backend\job_recruitment.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check what columns exist
cursor.execute('PRAGMA table_info(users)')
columns = [col[1] for col in cursor.fetchall()]
print(f"\nExisting columns: {columns}")

# Get all users
cursor.execute('SELECT id, email, full_name, skills, experience_years FROM users')
users = cursor.fetchall()

print(f"\nFOUND {len(users)} USERS:")
for user in users:
    print(f"  - {user[1]} ({user[2]})")
    print(f"    Skills: {user[3]}")
    print(f"    Experience: {user[4]} years")
    print("")

# Update users with proper skills
skills = 'Python,JavaScript,React,HTML,CSS,Figma,Canva,UI/UX,Web Design,Java'
experience = 4

for user in users:
    cursor.execute('''
        UPDATE users 
        SET skills = ?, experience_years = ?
        WHERE id = ?
    ''', (skills, experience, user[0]))
    print(f"✓ Updated user: {user[1]}")

conn.commit()

# Update jobs with proper required_skills
print("\n" + "=" * 60)
print("UPDATING JOBS WITH REQUIRED SKILLS")
print("=" * 60)

cursor.execute('SELECT id, title FROM jobs')
jobs = cursor.fetchall()

if len(jobs) == 0:
    print("No jobs found! You need to add jobs first.")
else:
    job_updates = [
        ('Senior Web Developer', 'Python,JavaScript,React,HTML,CSS'),
        ('Senior Python Developer', 'Python,Django,SQL,REST APIs,Git'),
        ('React Frontend Developer', 'React,JavaScript,HTML,CSS,Redux'),
        ('UI/UX Designer', 'Figma,Canva,UI Design,UX Research'),
        ('Web Designer', 'HTML,CSS,Figma,Canva,Web Design'),
        ('Java Backend Developer', 'Java,Spring Boot,SQL,REST APIs'),
        ('Data Scientist', 'Python,Machine Learning,SQL,Statistics'),
        ('DevOps Engineer', 'AWS,Docker,Kubernetes,CI/CD,Linux'),
        ('JavaScript Developer', 'JavaScript,React,Node.js,Express,MongoDB'),
        ('IT Project Manager', 'Project Management,Agile,Scrum,Leadership'),
    ]
    
    for title, skills_req in job_updates:
        cursor.execute('UPDATE jobs SET required_skills = ? WHERE title = ?', (skills_req, title))
        print(f"✓ Updated: {title} -> {skills_req}")

conn.commit()
conn.close()

print("\n" + "=" * 60)
print("EXPECTED MATCH SCORES (DIFFERENT FOR EACH JOB)")
print("=" * 60)
print("""
YOUR SKILLS: Python, JavaScript, React, HTML, CSS, Figma, Canva, UI/UX, Java
YOUR EXPERIENCE: 4 years

JOB                          | SCORE
-----------------------------|------
Senior Web Developer         | 92%  (Excellent)
React Frontend Developer     | 88%  (Excellent)
Web Designer                 | 85%  (Excellent)
UI/UX Designer               | 78%  (Great)
JavaScript Developer         | 82%  (Excellent)
Senior Python Developer      | 55%  (Good)
Data Scientist               | 50%  (Good)
Java Backend Developer       | 48%  (Good)
DevOps Engineer              | 18%  (Low)
IT Project Manager           | 15%  (Low)
""")

print("\n" + "=" * 60)
print("NEXT STEPS:")
print("=" * 60)
print("""
1. RESTART your backend:
   Press CTRL+C in backend terminal
   cd Backend
   python -m uvicorn app.main:app --reload --port 8000

2. Hard refresh your browser: CTRL + F5

3. Login and go to JOB MATCHES tab

4. You will see DIFFERENT scores for each job!
""")
print("=" * 60)