import requests

print("=" * 50)
print("SETUP NEW COMPANY AND POST JOBS")
print("=" * 50)

# Register new company
print("\n1. Registering new company...")
register_response = requests.post(
    'http://localhost:8000/api/auth/register/company',
    json={
        'company_name': 'Tech Solutions',
        'email': 'tech@solutions.com',
        'password': '123'
    }
)

if register_response.status_code == 200:
    company_data = register_response.json()
    company_id = company_data['user_id']
    print(f"✅ Company registered!")
    print(f"   Company ID: {company_id}")
    print(f"   Email: tech@solutions.com")
    print(f"   Password: 123")
    
    # Post jobs
    print("\n2. Posting jobs...")
    jobs = [
        {'title': 'Python Developer', 'description': 'Python dev needed', 'requirements': 'Python,Django,SQL', 'location': 'Remote', 'salary_range': '80k-100k', 'experience_required': 3},
        {'title': 'React Developer', 'description': 'React dev needed', 'requirements': 'React,JavaScript,HTML,CSS', 'location': 'Remote', 'salary_range': '70k-90k', 'experience_required': 2},
        {'title': 'Full Stack Developer', 'description': 'Full stack dev needed', 'requirements': 'Python,React,SQL', 'location': 'Remote', 'salary_range': '90k-120k', 'experience_required': 4},
    ]
    
    for job in jobs:
        response = requests.post(
            f'http://localhost:8000/api/company/jobs?company_id={company_id}',
            json=job
        )
        if response.status_code == 200:
            print(f"   ✅ {job['title']}")
        else:
            print(f"   ❌ {job['title']}: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("✅ SETUP COMPLETE!")
    print("=" * 50)
    print("\nLogin to Company Dashboard:")
    print("   URL: http://localhost:3000/company-dashboard.html")
    print("   Email: tech@solutions.com")
    print("   Password: 123")
    
else:
    print(f"❌ Registration failed: {register_response.text}")