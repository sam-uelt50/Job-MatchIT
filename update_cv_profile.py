import requests
import json

print("=" * 60)
print("UPDATING COMPLETE CV PROFILE")
print("=" * 60)

# Login
print("\n[1/3] Logging in...")
r = requests.post('http://localhost:8000/api/auth/login', 
                  json={'email': 'sam@test.com', 'password': '123456'})

if r.status_code != 200:
    print("❌ Login failed!")
    exit()

token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
print("✅ Login successful!")

# Complete CV Profile with ALL details
cv_profile = {
    # Personal Information
    'full_name': 'Samuel Tesema',
    'email': 'sam@test.com',
    'phone': '+251955595542',
    'location': 'Addis Ababa',
    'region': 'Addis Ababa',
    'city': 'Addis Ababa',
    'title': 'Full Stack Developer',
    'preferred_title': 'Senior Software Engineer',
    
    # Professional Summary
    'professional_summary': 'Experienced Full Stack Developer with 4+ years of experience building web applications. Expertise in Python, JavaScript, React, and Node.js. Strong background in AI and machine learning. Successfully developed resume evaluation systems, job recommendation platforms, and automation tools. Passionate about creating scalable solutions and mentoring junior developers.',
    
    # Industry & Specialization
    'industry_sector': 'Technology',
    'specialization_area': 'Full Stack Development',
    'professional_license': 'Software Engineering Professional',
    'license_number': 'SEP-2024-001',
    
    # Skills (Most Important)
    'skills': [
        'Python', 'JavaScript', 'React', 'Node.js', 'HTML', 'CSS',
        'FastAPI', 'Django', 'SQL', 'MongoDB', 'Git', 'Docker',
        'Machine Learning', 'NLP', 'API Development', 'TypeScript'
    ],
    
    # Experience
    'total_experience': 4,
    'years_in_ethiopia': 4,
    
    # Detailed Work Experience
    'experience_data': [
        {
            'title': 'Full Stack Developer',
            'company': 'Personal Projects',
            'location': 'Remote',
            'start_date': '2022-01',
            'end_date': '2025-12',
            'employment_type': 'Full-time',
            'description': 'Designed and developed AI-powered web applications including resume evaluation system with NLP, job recommendation platform with ML matching, and automation tools for workflow optimization.',
            'achievements': 'Built AI-based resume evaluation system used by 500+ users. Developed job recommendation platform achieving 85% accuracy. Created automation workflows improving productivity by 40%.'
        },
        {
            'title': 'Software Developer Intern',
            'company': 'Tech Solutions Ethiopia',
            'location': 'Addis Ababa',
            'start_date': '2021-01',
            'end_date': '2021-12',
            'employment_type': 'Internship',
            'description': 'Assisted in developing internal tools and web applications',
            'achievements': 'Contributed to 3 major projects. Learned agile development practices.'
        }
    ],
    
    # Education with Specialization
    'education_data': [
        {
            'degree': "Bachelor's Degree",
            'field': 'Computer Science',
            'institution': 'Hawassa University',
            'year': 2025,
            'gpa': '3.7/4.0',
            'specialization': 'Software Engineering',
            'achievements': 'Graduated with distinction, Dean\'s list for 4 semesters'
        }
    ],
    
    # Certifications
    'certification_data': [
        {'name': 'AWS Certified Developer', 'organization': 'Amazon', 'year': 2024},
        {'name': 'Meta Backend Developer', 'organization': 'Meta/Coursera', 'year': 2023},
        {'name': 'Python Institute Certification', 'organization': 'Python Institute', 'year': 2023}
    ],
    
    # Achievements
    'achievement_data': [
        'Best Project Award - University Tech Fair 2024',
        'Published research paper on AI-based recruitment',
        'Completed 10+ successful freelance projects'
    ],
    
    'publications': '"AI-Powered Resume Screening System" - Ethiopian Journal of Technology, 2024. "Job Recommendation Using NLP" - International Conference on AI, 2023.',
    
    # Languages
    'language_data': [
        {'name': 'English', 'proficiency': 'Fluent'},
        {'name': 'Amharic', 'proficiency': 'Native'},
        {'name': 'French', 'proficiency': 'Intermediate'}
    ],
    
    'memberships': 'IEEE Member, Ethiopian Software Engineers Association',
    'volunteer_work': 'Mentor at local coding bootcamp, Technical volunteer at tech conferences',
    
    # Job Preferences
    'expected_salary': 85000,
    'employment_type': 'Full-time',
    'willing_to_relocate': 'Yes',
    'notice_period': 30,
    
    # References
    'reference_name': 'Dr. Tekle Berhan',
    'reference_phone': '+251911223344',
    'reference_email': 'tekle@university.edu.et',
    'reference_relation': 'Professor and Thesis Advisor',
    
    # Portfolio
    'linkedin_url': 'https://linkedin.com/in/samuel-tesema',
    'github_url': 'https://github.com/samuel-tesema',
    'portfolio_url': 'https://samueltesema.dev'
}

print("\n[2/3] Saving CV profile to database...")
r = requests.post('http://localhost:8000/api/user/update-profile', json=cv_profile, headers=headers)

if r.status_code == 200:
    print("✅ CV Profile saved successfully!")
    print(f"   Skills: {len(cv_profile['skills'])} skills")
    print(f"   Experience: {cv_profile['total_experience']} years")
    print(f"   Education: {len(cv_profile['education_data'])} degrees")
    print(f"   Certifications: {len(cv_profile['certification_data'])}")
else:
    print(f"❌ Error: {r.status_code} - {r.text}")
    exit()

print("\n[3/3] Getting job recommendations...")
r = requests.get('http://localhost:8000/api/user/recommendations?limit=10', headers=headers)

if r.status_code == 200:
    data = r.json()
    jobs = data.get('recommendations', [])
    
    print("\n" + "=" * 70)
    print("🎯 JOB RECOMMENDATIONS BASED ON YOUR CV")
    print("=" * 70)
    
    for i, job in enumerate(jobs[:5], 1):
        score = job['match_score']
        if score >= 80:
            rating = "🏆 EXCELLENT"
        elif score >= 65:
            rating = "⭐ GREAT"
        elif score >= 50:
            rating = "👍 GOOD"
        else:
            rating = "📌 POTENTIAL"
        
        print(f"\n{i}. {job['job_title']} at {job['company']}")
        print(f"   📍 {job['location']} | 💰 {job['salary_range']}")
        print(f"   🎯 Match Score: {score}% - {rating}")
        print(f"   Required Skills: {job.get('required_skills', 'N/A')[:80]}...")
else:
    print(f"❌ Error getting recommendations: {r.status_code}")

print("\n" + "=" * 70)
print("✅ Complete! Now refresh your browser dashboard.")
print("=" * 70)