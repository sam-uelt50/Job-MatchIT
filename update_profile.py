import requests
import json

print("=" * 60)
print("UPDATING YOUR COMPLETE CV PROFILE")
print("=" * 60)

# Login
print("\n[1/3] Logging in...")
r = requests.post('http://localhost:8000/api/auth/login', 
                  json={'email': 'sam@test.com', 'password': '123456'})

if r.status_code != 200:
    print(f"❌ Login failed: {r.status_code}")
    exit()

token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
print("✅ Login successful!")

# Complete profile with ALL fields for comprehensive matching
profile = {
    'full_name': 'Samuel Tesema',
    'email': 'sam@test.com',
    'phone': '+251955595542',
    'location': 'Addis Ababa',
    'region': 'Addis Ababa',
    'city': 'Addis Ababa',
    'title': 'Full Stack Developer',
    'preferred_title': 'Senior Software Engineer',
    'professional_summary': 'Experienced Full Stack Developer with 4+ years experience in Python, JavaScript, React, and Node.js. Strong background in AI and machine learning. Passionate about building scalable web applications and mentoring junior developers.',
    'industry_sector': 'Technology',
    'specialization_area': 'Full Stack Development',
    'professional_license': 'Software Engineering Professional',
    'license_number': 'SEP-2024-001',
    'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'HTML', 'CSS', 'FastAPI', 'Django', 'SQL', 'MongoDB', 'Git', 'Docker', 'Machine Learning'],
    'total_experience': 4,
    'years_in_ethiopia': 4,
    'expected_salary': 85000,
    'employment_type': 'Full-time',
    'willing_to_relocate': 'Yes',
    'notice_period': 30,
    'linkedin_url': 'https://linkedin.com/in/samuel-tesema',
    'github_url': 'https://github.com/samuel-tesema',
    'portfolio_url': 'https://samueltesema.dev',
    'experience_data': [
        {
            'title': 'Full Stack Developer',
            'company': 'Personal Projects',
            'start_date': '2022-01',
            'end_date': '2025-12',
            'achievements': 'Built AI-based resume evaluation system used by 500+ users. Developed job recommendation platform achieving 85% accuracy. Created automation workflows improving productivity by 40%.'
        }
    ],
    'education_data': [
        {
            'degree': "Bachelor's Degree",
            'field': 'Computer Science',
            'institution': 'Hawassa University',
            'year': 2025,
            'gpa': '3.7/4.0',
            'specialization': 'Software Engineering'
        }
    ],
    'certification_data': [
        {'name': 'AWS Certified Developer', 'organization': 'Amazon', 'year': 2024},
        {'name': 'Python Institute Certification', 'organization': 'Python Institute', 'year': 2023}
    ],
    'achievement_data': [
        'Best Project Award - University Tech Fair 2024',
        'Published research paper on AI-based recruitment'
    ],
    'publications': 'AI-Powered Resume Screening System - Ethiopian Journal of Technology, 2024',
    'language_data': [
        {'name': 'English', 'proficiency': 'Fluent'},
        {'name': 'Amharic', 'proficiency': 'Native'}
    ],
    'memberships': 'IEEE Member, Ethiopian Software Engineers Association',
    'volunteer_work': 'Mentor at local coding bootcamp, Technical volunteer at tech conferences',
    'reference_name': 'Dr. Tekle Berhan',
    'reference_phone': '+251911223344',
    'reference_email': 'tekle@university.edu.et',
    'reference_relation': 'Professor and Thesis Advisor'
}

print("\n[2/3] Saving profile to database...")
r = requests.post('http://localhost:8000/api/user/update-profile', json=profile, headers=headers)

if r.status_code == 200:
    print("✅ Profile saved successfully!")
    print(f"   Skills: {len(profile['skills'])} skills")
    print(f"   Experience: {profile['total_experience']} years")
    print(f"   Education: {len(profile['education_data'])} degrees")
    print(f"   Certifications: {len(profile['certification_data'])}")
    print(f"   Languages: {len(profile['language_data'])}")
else:
    print(f"❌ Error: {r.status_code} - {r.text}")
    exit()

print("\n[3/3] Getting job recommendations...")
r = requests.get('http://localhost:8000/api/user/recommendations?limit=10', headers=headers)

if r.status_code == 200:
    data = r.json()
    jobs = data.get('recommendations', [])
    
    print("\n" + "=" * 60)
    print("🎯 JOB MATCHES (Based on ALL your CV fields)")
    print("=" * 60)
    print(f"\n📋 Your Profile Summary:")
    print(f"   Skills: {len(data['user'].get('skills', []))}")
    print(f"   Experience: {data['user'].get('experience_years', 0)} years")
    print(f"   Industry: {data['user'].get('industry', 'Not set')}")
    print(f"   Education: {data['user'].get('education_count', 0)} degrees")
    print(f"   Certifications: {data['user'].get('certification_count', 0)}")
    
    print("\n📊 Job Matches:")
    for job in jobs[:5]:
        score = job['match_score']
        if score >= 80:
            rating = "🏆 EXCELLENT"
        elif score >= 65:
            rating = "⭐ GREAT"
        elif score >= 50:
            rating = "👍 GOOD"
        else:
            rating = "📌 POTENTIAL"
        
        print(f"\n   {job['job_title']} at {job['company']}")
        print(f"   Match Score: {score}% - {rating}")
        print(f"   Required Skills: {job.get('required_skills', 'N/A')[:60]}...")
        
        breakdown = job.get('match_breakdown', {})
        if breakdown:
            print(f"   Breakdown: Skills:{breakdown.get('skills',0)}% | Exp:{breakdown.get('experience',0)}% | Edu:{breakdown.get('education',0)}%")
else:
    print(f"❌ Error getting recommendations: {r.status_code}")

print("\n" + "=" * 60)
print("✅ Complete! Now refresh your browser dashboard.")
print("=" * 60)