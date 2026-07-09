import requests

# Register company
print("Registering company...")
r = requests.post('http://localhost:8000/api/auth/register/company', 
                  json={'company_name': 'Tech Corp', 'email': 'company@test.com', 'password': '123'})
company = r.json()
print(f"Company ID: {company['user_id']}")

# Jobs to post
jobs = [
    {
        'title': 'Python Developer',
        'description': 'Looking for an experienced Python developer',
        'requirements': 'Python, Django, SQL, Git',
        'location': 'Remote',
        'salary_range': '$80k - $100k',
        'experience_required': 3
    },
    {
        'title': 'React Frontend Developer',
        'description': 'React specialist needed for frontend development',
        'requirements': 'React, JavaScript, HTML, CSS, Redux',
        'location': 'Remote',
        'salary_range': '$70k - $90k',
        'experience_required': 2
    },
    {
        'title': 'Full Stack Developer',
        'description': 'Full stack developer with Python and React',
        'requirements': 'Python, React, SQL, Git, Docker',
        'location': 'Remote',
        'salary_range': '$90k - $120k',
        'experience_required': 4
    },
    {
        'title': 'UI/UX Designer',
        'description': 'Creative designer for web applications',
        'requirements': 'Figma, Canva, UI/UX Design, Web Design',
        'location': 'Remote',
        'salary_range': '$60k - $80k',
        'experience_required': 2
    },
    {
        'title': 'AI/ML Engineer',
        'description': 'AI and Machine Learning engineer',
        'requirements': 'Python, AI, Machine Learning, TensorFlow',
        'location': 'Remote',
        'salary_range': '$100k - $140k',
        'experience_required': 4
    }
]

# Post each job
print("\nPosting jobs...")
for job in jobs:
    response = requests.post(f'http://localhost:8000/api/company/jobs?company_id={company["user_id"]}', json=job)
    if response.status_code == 200:
        print(f"✅ Posted: {job['title']}")
    else:
        print(f"❌ Failed: {job['title']} - {response.status_code}")

print("\n✅ All jobs posted successfully!")
print("\nNow go to your candidate dashboard and click 'Job Matches' tab to see recommendations based on your skills!")