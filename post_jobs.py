import requests

# Use the actual company ID from your registration
COMPANY_ID = 'e2b7d354-033b-4edb-ade8-35ca5c5c3767'

print("=" * 50)
print("POSTING TEST JOBS")
print("=" * 50)

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
        'title': 'React Developer',
        'description': 'Frontend React developer needed',
        'requirements': 'React, JavaScript, HTML, CSS',
        'location': 'Remote',
        'salary_range': '$70k - $90k',
        'experience_required': 2
    },
    {
        'title': 'Full Stack Developer',
        'description': 'Full stack developer with Python and React',
        'requirements': 'Python, React, SQL, Git',
        'location': 'Remote',
        'salary_range': '$90k - $120k',
        'experience_required': 4
    },
    {
        'title': 'UI/UX Designer',
        'description': 'Creative UI/UX designer needed',
        'requirements': 'Figma, Canva, UI/UX Design, Web Design',
        'location': 'Remote',
        'salary_range': '$60k - $80k',
        'experience_required': 2
    },
    {
        'title': 'Data Scientist',
        'description': 'Data scientist with ML experience',
        'requirements': 'Python, Machine Learning, SQL, TensorFlow',
        'location': 'Remote',
        'salary_range': '$100k - $140k',
        'experience_required': 4
    }
]

for job in jobs:
    try:
        response = requests.post(
            f'http://localhost:8000/api/company/jobs?company_id={COMPANY_ID}',
            json=job
        )
        if response.status_code == 200:
            print(f"✅ Posted: {job['title']}")
        else:
            print(f"❌ Failed: {job['title']} - {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error posting {job['title']}: {e}")

print("\n" + "=" * 50)
print("All jobs posted!")
print("=" * 50)