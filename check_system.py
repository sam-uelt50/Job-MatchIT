
import requests
import sqlite3
import os

print("=" * 70)
print("AI JOB MATCH PLATFORM - SYSTEM CHECK")
print("=" * 70)

# 1. Check Backend
print("\n[1/6] CHECKING BACKEND...")
try:
    r = requests.get("http://localhost:8000/health")
    if r.status_code == 200:
        print("   ✅ Backend is RUNNING")
    else:
        print("   ❌ Backend error")
except:
    print("   ❌ Backend NOT running")
    exit()

# 2. Check Database
print("\n[2/6] CHECKING DATABASE...")
db_path = r'C:\Users\Samuel\OneDrive\Desktop\JOB RECRUIMENT AND RECOMMEND\Backend\job_recruitment.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM jobs")
    jobs = cursor.fetchone()[0]
    print(f"   ✅ Users: {users}, Jobs: {jobs}")
    conn.close()
else:
    print("   ❌ Database not found")

# 3. Test Login
print("\n[3/6] TESTING LOGIN...")
login_data = {"email": "sam@test.com", "password": "123456"}
r = requests.post("http://localhost:8000/api/auth/login", json=login_data)
if r.status_code == 200:
    data = r.json()
    token = data.get("access_token")
    print(f"   ✅ Login successful")
    print(f"      User: {data.get('name')}")
else:
    print(f"   ❌ Login failed: {r.status_code}")
    token = None

# 4. Test Update Profile
print("\n[4/6] TESTING UPDATE PROFILE...")
if token:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    profile_data = {
        "skills": ["Python", "JavaScript", "React", "HTML", "CSS"],
        "total_experience": 4,
        "full_name": "Test User",
        "email": "sam@test.com"
    }
    r = requests.post("http://localhost:8000/api/user/update-profile", json=profile_data, headers=headers)
    if r.status_code == 200:
        print(f"   ✅ Profile updated: {r.json()}")
    else:
        print(f"   ❌ Failed: {r.status_code} - {r.text}")

# 5. Test Get Profile
print("\n[5/6] TESTING GET PROFILE...")
if token:
    r = requests.get("http://localhost:8000/api/user/profile", headers=headers)
    if r.status_code == 200:
        profile = r.json()
        print(f"   ✅ Profile: Skills: {profile.get('skills', [])}, Exp: {profile.get('experience_years', 0)}")
    else:
        print(f"   ❌ Failed: {r.status_code}")

# 6. Test Job Recommendations
print("\n[6/6] TESTING JOB RECOMMENDATIONS...")
if token:
    r = requests.get("http://localhost:8000/api/user/recommendations?limit=10", headers=headers)
    if r.status_code == 200:
        data = r.json()
        jobs = data.get("recommendations", [])
        print(f"   ✅ Found {len(jobs)} job matches")
        for job in jobs[:5]:
            print(f"      - {job['job_title']}: {job['match_score']}%")
    else:
        print(f"   ❌ Failed: {r.status_code} - {r.text}")

print("\n" + "=" * 70)
print("SYSTEM CHECK COMPLETE")
print("=" * 70)