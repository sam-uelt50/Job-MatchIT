import requests
import time

print("=" * 50)
print("Adding Jobs to AI Job Match Platform")
print("=" * 50)

# First, register or login company
register_data = {
    'company_name': 'Tech Corp',
    'email': 'tech@corp.com',
    'password': '123456'
}

company_id = None

# Try to register
try:
    r = requests.post('http://localhost:8000/api/auth/register/company', json=register_data)
    if r.status_code == 200:
        company = r.json()
        company_id = company['user_id']
        print(f"✓ Company registered successfully! ID: {company_id}")
    else:
        # Try to login instead
        r = requests.post('http://localhost:8000/api/auth/login', json={'email': 'tech@corp.com', 'password': '123456'})
        if r.status_code == 200:
            company = r.json()
            company_id = company['user_id']
            print(f"✓ Company logged in! ID: {company_id}")
        else:
            print(f"✗ Failed to create/login company: {r.text}")
            exit()
except Exception as e:
    print(f"✗ Error connecting to backend: {e}")
    print("Make sure backend is running on port 8000")
    exit()

if not company_id:
    print("✗ No company ID available")
    exit()

# Jobs with proper skills for matching
jobs = [
    {
        'title': 'Senior Web Developer',
        'description': 'Looking for an experienced full-stack web developer',
        'requirements': 'Build responsive web applications using modern frameworks',
        'required_skills': 'HTML, CSS, JavaScript, React, Python, Django',
        'location': 'Remote',
        'salary_range': '80k-120k',
        'employment_type': 'full-time',
        'experience_required': 3
    },
    {
        'title': 'Web Designer',
        'description': 'Creative web designer for modern websites',
        'requirements': 'Design beautiful and responsive websites',
        'required_skills': 'UI/UX Design, Figma, Canva, HTML, CSS, JavaScript',
        'location': 'Remote',
        'salary_range': '60k-90k',
        'employment_type': 'full-time',
        'experience_required': 2
    },
    {
        'title': 'Python Developer',
        'description': 'Backend API development with Python',
        'requirements': 'Build scalable backend services',
        'required_skills': 'Python, Django, Flask, SQL, APIs, PostgreSQL',
        'location': 'Remote',
        'salary_range': '90k-130k',
        'employment_type': 'full-time',
        'experience_required': 3
    },
    {
        'title': 'React Frontend Developer',
        'description': 'Frontend development with React',
        'requirements': 'Build modern single-page applications',
        'required_skills': 'React, JavaScript, HTML, CSS, Redux, TypeScript',
        'location': 'Remote',
        'salary_range': '70k-110k',
        'employment_type': 'full-time',
        'experience_required': 2
    },
    {
        'title': 'Data Entry Specialist',
        'description': 'Remote data entry position',
        'requirements': 'Accurate data entry and management',
        'required_skills': 'Typing, Excel, Data Entry, Microsoft Office',
        'location': 'Remote',
        'salary_range': '30k-45k',
        'employment_type': 'full-time',
        'experience_required': 1
    },
    {
        'title': 'Full Stack Developer',
        'description': 'Full stack development for web applications',
        'requirements': 'Work on both frontend and backend',
        'required_skills': 'JavaScript, React, Node.js, Python, SQL, MongoDB',
        'location': 'Remote',
        'salary_range': '85k-125k',
        'employment_type': 'full-time',
        'experience_required': 3
    },
    {
        'title': 'UI/UX Designer',
        'description': 'User interface and experience design',
        'requirements': 'Create amazing user experiences',
        'required_skills': 'UI/UX Design, Figma, Adobe XD, Sketch, User Research',
        'location': 'Remote',
        'salary_range': '65k-95k',
        'employment_type': 'full-time',
        'experience_required': 2
    },
    {
        'title': 'DevOps Engineer',
        'description': 'Cloud infrastructure and deployment',
        'requirements': 'Manage cloud infrastructure',
        'required_skills': 'AWS, Docker, Kubernetes, Jenkins, CI/CD, Linux',
        'location': 'Remote',
        'salary_range': '100k-150k',
        'employment_type': 'full-time',
        'experience_required': 4
    }
]

print("\n" + "=" * 50)
print("Adding Jobs to Database")
print("=" * 50)

success_count = 0
fail_count = 0

for job in jobs:
    try:
        r = requests.post(f'http://localhost:8000/api/company/jobs?company_id={company_id}', json=job)
        if r.status_code == 200:
            print(f"  ✓ SUCCESS: {job['title']}")
            success_count += 1
        else:
            print(f"  ✗ FAILED: {job['title']} - {r.text}")
            fail_count += 1
    except Exception as e:
        print(f"  ✗ ERROR: {job['title']} - {e}")
        fail_count += 1
    time.sleep(0.5)  # Small delay to avoid overwhelming the server

print("\n" + "=" * 50)
print("SUMMARY")
print("=" * 50)
print(f"✓ Successfully added: {success_count} jobs")
print(f"✗ Failed: {fail_count} jobs")
print("\nYou can now login to the candidate dashboard and see job matches!")