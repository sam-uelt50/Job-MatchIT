import sqlite3

print("=" * 60)
print("SAVING PROFILE TO DATABASE")
print("=" * 60)

db_path = r'C:\Users\Samuel\OneDrive\Desktop\JOB RECRUIMENT AND RECOMMEND\Backend\job_recruitment.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# YOUR COMPLETE PROFILE DATA
full_name = 'Samuel Tesema'
email1 = 'samuel.tesema@example.com'
email2 = 'sam@test.com'
phone = '+251955595542'
location = 'Addis Ababa, Ethiopia'
headline = 'AI Automation & Full Stack Developer | Electrical & Computer Engineering Student'
bio = 'Passionate AI Automation and Full Stack Developer with experience in web development, NLP-based systems, and automation projects. Currently studying Electrical and Computer Engineering with strong interests in machine learning, AI-powered applications, and scalable software systems.'

# Your skills
skills = [
    'Python', 'JavaScript', 'React', 'Node.js', 'FastAPI', 
    'HTML', 'CSS', 'Tailwind', 'SQL', 'MySQL', 'MongoDB',
    'Machine Learning', 'NLP', 'API Development', 'Git', 'GitHub'
]
skills_str = ','.join(skills)

# Experience
experience_years = 4

print(f"\n📋 Profile Data to Save:")
print(f"   Name: {full_name}")
print(f"   Email: {email1} and {email2}")
print(f"   Skills: {skills_str}")
print(f"   Experience: {experience_years} years")

# Update first user
cursor.execute('''
    UPDATE users 
    SET full_name = ?, phone = ?, location = ?, 
        skills = ?, experience_years = ?, headline = ?, bio = ?
    WHERE email = ?
''', (full_name, phone, location, skills_str, experience_years, headline, bio, email1))

# Update second user (sam@test.com)
cursor.execute('''
    UPDATE users 
    SET full_name = ?, phone = ?, location = ?, 
        skills = ?, experience_years = ?, headline = ?, bio = ?
    WHERE email = ?
''', (full_name, phone, location, skills_str, experience_years, headline, bio, email2))

conn.commit()

print("\n✅ Profile saved successfully!")

# Verify
cursor.execute('SELECT full_name, skills, experience_years FROM users WHERE email = ?', (email2,))
user = cursor.fetchone()
if user:
    print(f"\n📌 VERIFIED - Database now has:")
    print(f"   Name: {user[0]}")
    print(f"   Skills: {user[1][:80]}...")
    print(f"   Experience: {user[2]} years")

conn.close()
print("\n" + "=" * 60)