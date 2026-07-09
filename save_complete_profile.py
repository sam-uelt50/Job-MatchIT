import sqlite3

print("=" * 70)
print("SAVING COMPLETE PROFILE TO DATABASE")
print("=" * 70)

db_path = r'C:\Users\Samuel\OneDrive\Desktop\JOB RECRUIMENT AND RECOMMEND\Backend\job_recruitment.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# ============ YOUR COMPLETE PROFILE DATA FROM THE FORM ============

# Personal Information
full_name = 'Samuel Tesema'
email = 'samueltesema56@gmail.com'
phone = '+251955595542'
location = 'Addis Abeba'
headline = 'AI Automation & Full Stack Developer | Electrical & Computer Engineering Student'
bio = '''Passionate AI Automation and Full Stack Developer with experience in web development, NLP-based systems, and automation projects. Currently studying Electrical and Computer Engineering with strong interests in machine learning, AI-powered applications, and scalable software systems. Skilled in building intelligent solutions including resume evaluation systems, job recommendation platforms, and modern responsive web applications. Seeking remote opportunities to apply AI and software engineering skills to solve real-world problems.'''

# Technical Skills (70% of Match Score)
skills = [
    'Python', 'JavaScript', 'React', 'Node.js', 'FastAPI',
    'HTML', 'CSS', 'Tailwind', 'SQL', 'MySQL', 'MongoDB',
    'Machine Learning', 'NLP', 'API Development', 'Git', 'GitHub',
    'Problem Solving', 'Communication', 'Teamwork'
]
skills_str = ','.join(skills)

# Work Experience
experience_years = 4
employment_status = 'Employed Part-time'
current_salary = 20000

# Work Experience Details
work_experiences = [
    {
        'title': 'Full Stack Developer',
        'company': 'Personal Projects',
        'location': 'Remote',
        'start_date': '2022-01',
        'end_date': '2025-12',
        'employment_type': 'Full-time',
        'description': 'Designed and developed AI-powered web applications including resume evaluation systems, job recommendation platforms, and automation tools. Built responsive frontend interfaces and backend APIs while integrating machine learning and NLP techniques for intelligent matching systems.',
        'achievements': '''• Developed AI-based resume evaluation and job recommendation platform
• Built responsive full stack web applications using React and FastAPI
• Implemented NLP and semantic matching for intelligent job recommendations
• Created automation workflows to improve productivity and user experience
• Designed modern UI dashboards for recruiters and job seekers''',
        'technologies': 'Python, React, FastAPI, Machine Learning, NLP, JavaScript, SQL, GitHub'
    }
]

# Education
educations = [
    {
        'degree': 'Bachelor',
        'field': 'Electrical and Computer Engineering',
        'institution': 'Hawassa University',
        'graduation_year': 2025,
        'gpa': '3.5/4.0',
        'coursework': 'Artificial Intelligence, Database Systems, Programming Fundamentals, Computer Networks, Embedded Systems, Digital Systems Design, Web Development, Machine Learning Fundamentals'
    }
]

# Job Preferences
desired_title = 'AI Engineer / Full Stack Developer / ML Engineer'
preferred_industry = 'Technology'
employment_type = 'Part-time'
expected_salary = 20000
preferred_location = 'Addis Abeba'
remote_preference = 'Fully Remote'

# ============ UPDATE DATABASE ============

# Update user with email 'sam@test.com' (your login email)
cursor.execute('''
    UPDATE users 
    SET full_name = ?, 
        phone = ?, 
        location = ?, 
        skills = ?, 
        experience_years = ?,
        headline = ?,
        bio = ?
    WHERE email = 'sam@test.com'
''', (full_name, phone, location, skills_str, experience_years, headline, bio))

# Also update with your gmail if exists
cursor.execute('''
    UPDATE users 
    SET full_name = ?, 
        phone = ?, 
        location = ?, 
        skills = ?, 
        experience_years = ?,
        headline = ?,
        bio = ?
    WHERE email = ?
''', (full_name, phone, location, skills_str, experience_years, headline, bio, email))

conn.commit()

print("\n✅ PROFILE SAVED TO DATABASE!")
print("=" * 60)
print(f"Name: {full_name}")
print(f"Email (login): sam@test.com")
print(f"Skills: {skills_str[:100]}...")
print(f"Experience: {experience_years} years")
print(f"Headline: {headline}")
print(f"Bio: {bio[:100]}...")

# Verify
cursor.execute('SELECT full_name, skills, experience_years FROM users WHERE email = "sam@test.com"')
user = cursor.fetchone()
if user:
    print(f"\n📌 VERIFIED - Database now has:")
    print(f"   Name: {user[0]}")
    print(f"   Skills: {user[1][:80]}...")
    print(f"   Experience: {user[2]} years")

conn.close()
print("\n" + "=" * 70)
print("✅ Profile saved successfully! Now run the add_jobs.py script")
print("=" * 70)