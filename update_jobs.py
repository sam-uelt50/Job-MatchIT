import sqlite3

print("=" * 60)
print("UPDATING JOBS WITH REQUIRED SKILLS")
print("=" * 60)

db_path = r'C:\Users\Samuel\OneDrive\Desktop\JOB RECRUIMENT AND RECOMMEND\Backend\job_recruitment.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Update jobs with proper required_skills
jobs_to_update = [
    ('Full Stack Developer', 'Python,React,JavaScript,Node.js,MongoDB'),
    ('JavaScript Developer', 'JavaScript,React,Node.js,Express'),
    ('React Frontend Developer', 'React,JavaScript,HTML,CSS,Redux'),
    ('ML Engineer', 'Python,Machine Learning,TensorFlow,NLP'),
    ('Data Scientist', 'Python,Machine Learning,SQL,Statistics'),
    ('Senior Python Developer', 'Python,Django,SQL,REST APIs'),
    ('Backend Developer', 'Python,FastAPI,SQL,MongoDB'),
    ('UI/UX Designer', 'Figma,Adobe XD,UI Design,UX Research'),
    ('Java Developer', 'Java,Spring Boot,SQL,REST APIs'),
    ('DevOps Engineer', 'AWS,Docker,Kubernetes,CI/CD,Linux')
]

for title, skills in jobs_to_update:
    cursor.execute('UPDATE jobs SET required_skills = ? WHERE title = ?', (skills, title))
    print(f'✅ Updated: {title}')
    print(f'   Skills: {skills}')
    print()

conn.commit()
conn.close()

print("=" * 60)
print("✅ JOBS UPDATED SUCCESSFULLY!")
print("=" * 60)