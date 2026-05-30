# 🎯 JobMatch ET - AI-Powered Job Matching Platform for Ethiopia

## 📌 Overview
AI-powered recruitment platform using **Random Forest Machine Learning** with **78.5% accuracy** to match job seekers with employers.

## 🚀 Features
- 🤖 **AI-Powered Matching** - Random Forest ML with 78.5% accuracy
- 📊 **4-Factor Scoring** - Skills (40%) + Experience (25%) + NLP (20%) + Education (15%)
- 👨‍💼 **Candidate Portal** - Profile, skill suggestions, apply to jobs
- 🏢 **Employer Portal** - Post jobs, rank candidates
- 👑 **Admin Dashboard** - User & job management
- 📄 **CV Upload** - Share CV with employers

## 📊 System Performance
| Metric | Value |
|--------|-------|
| Training Data | 41,953 job postings |
| ML Accuracy | 78.5% |
| Precision | 82% |
| SUS Score | 78.4 (Good+) |

## 🛠️ Tech Stack
- **Backend**: FastAPI, Python, JWT, SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **ML**: Random Forest, NLP
- **Auth**: JWT + bcrypt

## 🚀 Quick Start
`ash
# Backend
cd Backend
pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt] python-multipart
python -m uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
python -m http.server 3000


