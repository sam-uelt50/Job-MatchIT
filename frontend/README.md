
# 🎯 JobMatch ET - AI-Powered Job Matching Platform 🇪🇹

![JobMatch ET](./screenshots/landing-page.png)


[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge\&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge\&logo=python\&logoColor=white)](https://python.org)
[![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge\&logo=sqlite\&logoColor=white)](https://sqlite.org)
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge\&logo=html5\&logoColor=white)](https://html.spec.whatwg.org/)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge\&logo=css3\&logoColor=white)](https://www.w3.org/Style/CSS/)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge\&logo=javascript\&logoColor=black)](https://javascript.com)

---

# 📌 Overview

**JobMatch ET** is an AI-powered recruitment platform designed to improve job discovery and hiring efficiency in the Ethiopian employment market.

The platform uses **Machine Learning, Natural Language Processing (NLP), and intelligent ranking algorithms** to match candidates with suitable job opportunities based on their skills, experience, education, and job requirements.

The system provides separate experiences for:

* 👨‍💻 Job Seekers
* 🏢 Employers
* 👑 Administrators

---

# ✨ Features

| Feature                 | Description                                                                     |
| ----------------------- | ------------------------------------------------------------------------------- |
| 🤖 AI Job Matching      | Random Forest ML model recommends suitable jobs for candidates                  |
| 📊 Smart Ranking System | Multi-factor scoring based on skills, experience, NLP similarity, and education |
| 👨‍💻 Candidate Portal  | Create profiles, upload CVs, receive job recommendations, apply for jobs        |
| 🏢 Employer Portal      | Create job posts, view applicants, rank candidates                              |
| 👑 Admin Dashboard      | Manage users, jobs, and system statistics                                       |
| 📄 CV Management        | Upload and share candidate CV information                                       |
| 🧠 NLP Matching         | Analyze job descriptions and candidate profiles                                 |
| 🔐 Authentication       | Secure JWT-based authentication with password hashing                           |

---

# 🧠 Artificial Intelligence System

## Machine Learning Model

**Algorithm:** Random Forest Classifier

### Matching Factors:

| Factor                  | Weight |
| ----------------------- | -----: |
| Skills Matching         |    40% |
| Experience Matching     |    25% |
| NLP Semantic Similarity |    20% |
| Education Matching      |    15% |

## Model Performance

| Metric           |                Result |
| ---------------- | --------------------: |
| Training Dataset |    41,953 Job Records |
| Accuracy         |                 78.5% |
| Precision        |                   82% |
| SUS Score        | 78.4 (Good Usability) |

---

# 🏗️ System Architecture

```
                 User
                  |
                  |
        ----------------------
        |                    |
 Candidate Portal      Employer Portal
        |                    |
        ----------------------
                  |
            Frontend Layer
        HTML + CSS + JavaScript
                  |
                  |
            FastAPI Backend
                  |
        ---------------------
        |                   |
     SQLite DB          ML Engine
                            |
                    Random Forest Model
                            |
                     Job Recommendations
```

---

# 🛠️ Technology Stack

## Backend

* Python
* FastAPI
* JWT Authentication
* SQLite Database
* REST API

## Frontend

* HTML5
* CSS3
* JavaScript

## Artificial Intelligence

* Scikit-learn
* Random Forest
* NLP Similarity Analysis

## Security

* JWT Authentication
* bcrypt Password Hashing

---

# 🚀 Installation & Setup

## Prerequisites

* Python 3.10+
* pip package manager
* Git

---

## Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/JobMatch-ET.git

cd JobMatch-ET
```

---

# Backend Setup

```bash
cd Backend

pip install -r requirements.txt

python -m uvicorn app.main:app --reload --port 8000
```

Backend will run:

```
http://localhost:8000
```

API Documentation:

```
http://localhost:8000/docs
```

---

# Frontend Setup

Open another terminal:

```bash
cd frontend

python -m http.server 3000
```

Frontend:

```
http://localhost:3000
```

---

# 📡 Main API Endpoints

| Endpoint                    | Description             |
| --------------------------- | ----------------------- |
| `/api/auth/login`           | User authentication     |
| `/api/user/profile`         | Candidate profile       |
| `/api/user/recommendations` | AI job recommendations  |
| `/api/user/apply/{job_id}`  | Apply for jobs          |
| `/api/company/jobs`         | Employer job management |
| `/api/admin/stats`          | System statistics       |

---


# 📸 Screenshots

## Landing Page

![Landing Page](./screenshots/landing-page.png)


## AI Job Matching Dashboard

![AI Jobmatch Dashboard](./screenshots/ai-jobmatch-dashboard.png)


## Job Seeker Dashboard

![Job Seeker Dashboard](./screenshots/jobseeker-dashboard.png)


## Employer Dashboard

![Employer Dashboard](./screenshots/employer-dashboard.png)


## Job Posting Dashboard

![Job Post Dashboard](./screenshots/job-post-dashboard.png)


## Application Dashboard

![Application Dashboard](./screenshots/application-dashboard.png)

# 🌐 Deployment

Production deployment:

* Frontend: Netlify
* Backend: Render
* Database: SQLite

---

# 🎯 Project Goals

JobMatch ET aims to:

✅ Reduce difficulty of finding relevant jobs
✅ Help employers discover qualified candidates faster
✅ Apply AI techniques to local employment challenges
✅ Demonstrate practical use of Machine Learning in recruitment technology

---

# 🔮 Future Improvements

* Deep Learning recommendation model
* Real-time notifications
* LinkedIn profile integration
* Advanced CV parsing using AI
* Mobile application
* Multilingual support (English / Amharic)

---

# 👨‍💻 Developer

**Samuel Tesema**

Electrical and Computer Engineering Student

Interested in:

* Artificial Intelligence
* Machine Learning
* Full-Stack Development
* Automation Systems

---

⭐ If you find this project useful, consider giving it a star.
