import sqlite3
import pandas as pd
import uuid
from datetime import datetime
import os
import random

print("=" * 60)
print("LOADING DATASET INTO DATABASE")
print("=" * 60)

DB_PATH = r'C:\Users\Samuel\OneDrive\Desktop\JOB RECRUIMENT AND RECOMMEND\Backend\job_recruitment.db'

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Clear existing jobs (optional - comment out if you want to keep existing)
cursor.execute("DELETE FROM jobs")
print("✓ Cleared existing jobs")

# Load Ethiopian dataset
if os.path.exists('ethiopian_jobs_dataset.csv'):
    df = pd.read_csv('ethiopian_jobs_dataset.csv')
    print(f"✓ Loaded {len(df)} jobs from ethiopian_jobs_dataset.csv")
else:
    print("❌ Dataset file not found. Run create_ethiopian_dataset.py first!")
    exit()

# Insert jobs into database
inserted = 0
for index, row in df.iterrows():
    job_id = str(uuid.uuid4())
    
    title = row['title']
    company = row['company']
    location = row['location']
    skills = row['required_skills']
    description = row['description']
    salary = row['salary_range']
    experience = int(row['experience_required'])
    industry = row['industry']
    employment_type = row['employment_type']
    
    cursor.execute('''
        INSERT INTO jobs (id, title, company_name, location, required_skills, description, salary_range, experience_required, industry, employment_type, created_at, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (job_id, title, company, location, skills, description, salary, experience, industry, employment_type, datetime.now().isoformat(), 'active'))
    inserted += 1
    
    if (index + 1) % 50 == 0:
        print(f"   Inserted {index + 1} jobs...")

conn.commit()
conn.close()

print(f"\n✅ Successfully inserted {inserted} jobs into database!")

# Verify
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM jobs")
count = cursor.fetchone()[0]
cursor.execute("SELECT industry, COUNT(*) FROM jobs GROUP BY industry")
industries = cursor.fetchall()
conn.close()

print(f"\n📊 Database Summary:")
print(f"   Total jobs in database: {count}")
print("\n   Jobs by Industry:")
for industry, job_count in industries:
    print(f"     - {industry}: {job_count} jobs")