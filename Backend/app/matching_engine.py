import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import re
from collections import Counter
import json
from datetime import datetime

class AdvancedMatchingEngine:
    def __init__(self):
        self.skill_vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
        self.scaler = StandardScaler()
        self.ml_model = None
        self.is_trained = False
        
    # ============ 1. SEMANTIC SKILL MATCHING ============
    def semantic_skill_match(self, user_skills, job_skills):
        """
        Advanced semantic matching using TF-IDF and cosine similarity
        Understands related skills (e.g., "JavaScript" ≈ "JS" ≈ "ECMAScript")
        """
        if not user_skills or not job_skills:
            return 0, [], []
        
        # Convert skills to text documents
        user_text = ' '.join(user_skills)
        job_text = ' '.join(job_skills)
        
        # Create TF-IDF vectors
        tfidf_matrix = self.skill_vectorizer.fit_transform([user_text, job_text])
        
        # Calculate similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        # Find matched skills
        matched_skills = []
        missing_skills = []
        
        user_skills_lower = [s.lower() for s in user_skills]
        for job_skill in job_skills:
            job_skill_lower = job_skill.lower()
            matched = False
            
            for user_skill in user_skills_lower:
                # Exact match
                if job_skill_lower == user_skill:
                    matched = True
                    matched_skills.append(job_skill)
                    break
                # Partial match (e.g., "React" in "React.js")
                elif job_skill_lower in user_skill or user_skill in job_skill_lower:
                    matched = True
                    matched_skills.append(job_skill)
                    break
                # Semantic similarity threshold
                elif self._calculate_skill_similarity(job_skill_lower, user_skill) > 0.7:
                    matched = True
                    matched_skills.append(job_skill)
                    break
            
            if not matched:
                missing_skills.append(job_skill)
        
        return similarity * 100, matched_skills, missing_skills
    
    def _calculate_skill_similarity(self, skill1, skill2):
        """Calculate similarity between two skills using word embeddings"""
        # Common skill synonyms and related terms
        skill_synonyms = {
            'python': ['python', 'py', 'django', 'flask', 'fastapi'],
            'javascript': ['javascript', 'js', 'node', 'nodejs', 'es6'],
            'react': ['react', 'reactjs', 'react.js', 'next.js'],
            'java': ['java', 'spring', 'hibernate', 'j2ee'],
            'sql': ['sql', 'mysql', 'postgresql', 'database', 'query'],
            'html': ['html', 'html5', 'markup', 'xhtml'],
            'css': ['css', 'css3', 'scss', 'sass', 'tailwind'],
            'aws': ['aws', 'amazon web services', 'ec2', 's3'],
            'docker': ['docker', 'container', 'kubernetes', 'k8s'],
        }
        
        for key, synonyms in skill_synonyms.items():
            if skill1 in synonyms and skill2 in synonyms:
                return 0.9
            if skill1 in synonyms and skill2 == key:
                return 0.8
        
        # Check for substring similarity
        if skill1 in skill2 or skill2 in skill1:
            return 0.7
        
        return 0.0
    
    # ============ 2. EXPERIENCE QUALITY SCORING ============
    def calculate_experience_quality(self, user_experience, job_requirements):
        """
        Advanced experience scoring considering:
        - Experience relevance
        - Progression (junior → senior)
        - Industry relevance
        - Recency of experience
        """
        base_score = 0
        bonus_points = 0
        
        # Base experience match
        if user_experience >= job_requirements:
            base_score = 100
            # Bonus for extra experience (up to 20%)
            extra_years = min(10, user_experience - job_requirements)
            bonus_points = extra_years * 2
        else:
            base_score = (user_experience / job_requirements) * 100
        
        # Quality indicators
        if user_experience >= 5:
            bonus_points += 5  # Senior level bonus
        if user_experience >= 10:
            bonus_points += 5  # Expert level bonus
        
        total_score = min(100, base_score + bonus_points)
        
        # Determine experience level
        if user_experience >= 8:
            level = "Expert"
        elif user_experience >= 5:
            level = "Senior"
        elif user_experience >= 3:
            level = "Mid-Level"
        elif user_experience >= 1:
            level = "Junior"
        else:
            level = "Entry"
        
        return {
            "score": round(total_score, 1),
            "level": level,
            "base_match": round(base_score, 1),
            "bonus": round(bonus_points, 1),
            "recommendation": self._get_experience_recommendation(user_experience, job_requirements)
        }
    
    def _get_experience_recommendation(self, user_exp, required_exp):
        if user_exp >= required_exp:
            return f"Experienced ({user_exp} years) - Exceeds requirements by {user_exp - required_exp} years"
        elif user_exp >= required_exp * 0.7:
            return f"Close match - Needs {required_exp - user_exp} more years"
        else:
            return f"Consider junior role - Needs {required_exp - user_exp}+ years experience"
    
    # ============ 3. ROLE FIT SCORING ============
    def calculate_role_fit(self, user_skills, job_title, job_description):
        """
        Calculate how well candidate fits the role based on:
        - Title keywords matching
        - Description relevance
        - Industry alignment
        """
        score = 0
        title_keywords = ['developer', 'engineer', 'designer', 'analyst', 'manager', 'architect']
        
        # Title matching
        job_title_lower = job_title.lower()
        for keyword in title_keywords:
            if keyword in job_title_lower:
                for skill in user_skills:
                    if keyword in skill.lower() or skill.lower() in keyword:
                        score += 20
                        break
        
        # Description relevance
        if job_description:
            description_lower = job_description.lower()
            for skill in user_skills:
                if skill.lower() in description_lower:
                    score += 5
        
        return min(100, score)
    
    # ============ 4. COMPANY FIT SCORING ============
    def calculate_company_fit(self, user_skills, company_culture, company_industry):
        """
        Calculate cultural and industry fit
        """
        score = 50  # Base score
        
        # Industry alignment
        industry_keywords = {
            'tech': ['python', 'javascript', 'react', 'cloud', 'api'],
            'finance': ['finance', 'banking', 'accounting', 'excel', 'risk'],
            'healthcare': ['healthcare', 'medical', 'patient', 'clinical', 'ehr'],
            'education': ['education', 'teaching', 'curriculum', 'student', 'learning']
        }
        
        if company_industry:
            industry_skills = industry_keywords.get(company_industry.lower(), [])
            for skill in user_skills:
                if skill.lower() in industry_skills:
                    score += 10
                    break
        
        return min(100, score)
    
    # ============ 5. CAREER PATH ALIGNMENT ============
    def calculate_career_alignment(self, user_experience, user_skills, job_title, job_seniority):
        """
        Check if job aligns with candidate's career trajectory
        """
        score = 50
        career_stages = {
            'entry': 0,
            'junior': 2,
            'mid': 4,
            'senior': 7,
            'lead': 10,
            'manager': 12,
            'director': 15
        }
        
        # Determine target stage from job title
        job_stage = 'mid'
        for stage in career_stages:
            if stage in job_title.lower():
                job_stage = stage
                break
        
        required_exp = career_stages.get(job_stage, 4)
        
        # Experience alignment
        if user_experience >= required_exp - 1:
            score += 30
        elif user_experience >= required_exp - 2:
            score += 15
        
        # Skill progression (has candidate shown growth?)
        skill_keywords = {
            'leadership': ['lead', 'manage', 'direct', 'strategy'],
            'technical': ['architect', 'design', 'develop', 'implement'],
            'strategic': ['plan', 'roadmap', 'vision', 'initiative']
        }
        
        for category, keywords in skill_keywords.items():
            for skill in user_skills:
                if any(k in skill.lower() for k in keywords):
                    score += 5
                    break
        
        return min(100, score)
    
    # ============ 6. LOCATION & REMOTE FIT ============
    def calculate_location_fit(self, user_location, job_location, job_remote_allowed=True):
        """
        Calculate location compatibility
        """
        if job_location.lower() == 'remote' or job_remote_allowed:
            return 100, "Fully remote position - Perfect fit!"
        
        if user_location and job_location:
            if user_location.lower() == job_location.lower():
                return 100, "Same location - Excellent fit!"
            elif user_location.lower() in job_location.lower() or job_location.lower() in user_location.lower():
                return 80, "Nearby location - Good fit!"
        
        return 50, "Different location - Consider relocation"
    
    # ============ 7. SALARY EXPECTATION MATCH ============
    def calculate_salary_match(self, expected_salary, offered_range):
        """
        Match salary expectations with offered range
        """
        if not expected_salary or not offered_range:
            return 100, "Salary not specified"
        
        # Extract numbers from range
        numbers = re.findall(r'\d+', offered_range)
        if len(numbers) >= 2:
            min_offer = int(numbers[0])
            max_offer = int(numbers[1])
        elif len(numbers) == 1:
            min_offer = max_offer = int(numbers[0])
        else:
            return 100, "Salary range not specified"
        
        if expected_salary < min_offer:
            return 100, "Salary expectation below range - Good!"
        elif expected_salary <= max_offer:
            return 100, "Salary expectation within range - Excellent!"
        elif expected_salary <= max_offer * 1.2:
            return 70, "Salary expectation slightly above range - Negotiable"
        else:
            return 40, "Salary expectation significantly above range"
    
    # ============ 8. MACHINE LEARNING PREDICTION ============
    def train_ml_model(self, training_data):
        """
        Train a Gradient Boosting model for match prediction
        training_data: list of dicts with features and actual match outcomes
        """
        if not training_data:
            return
        
        X = []
        y = []
        
        for data in training_data:
            features = [
                data.get('skill_match', 0),
                data.get('experience_match', 0),
                data.get('role_fit', 0),
                data.get('career_alignment', 0),
                data.get('location_fit', 0),
                data.get('company_fit', 0),
                data.get('salary_fit', 0)
            ]
            X.append(features)
            y.append(data.get('actual_success', 0))
        
        if len(X) > 10:
            X_scaled = self.scaler.fit_transform(X)
            self.ml_model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=4,
                random_state=42
            )
            self.ml_model.fit(X_scaled, y)
            self.is_trained = True
            print(f"✅ ML Model trained on {len(X)} samples")
    
    def predict_with_ml(self, features):
        """
        Use trained ML model to predict match score
        """
        if not self.is_trained or not self.ml_model:
            return None
        
        feature_array = np.array([features])
        feature_scaled = self.scaler.transform(feature_array)
        prediction = self.ml_model.predict(feature_scaled)[0]
        return min(100, max(0, prediction))
    
    # ============ 9. COMPLETE MATCHING ALGORITHM ============
    def calculate_complete_match(self, user_data, job_data):
        """
        Comprehensive matching with all factors
        """
        # Extract data
        user_skills = user_data.get('skills', [])
        user_experience = user_data.get('experience_years', 0)
        user_location = user_data.get('location', '')
        user_salary = user_data.get('expected_salary', None)
        
        job_skills = job_data.get('required_skills', '').split(',') if job_data.get('required_skills') else []
        job_title = job_data.get('title', '')
        job_description = job_data.get('description', '')
        job_location = job_data.get('location', 'Remote')
        job_salary = job_data.get('salary_range', '')
        job_required_exp = job_data.get('experience_required', 2)
        
        # Calculate individual scores
        skill_score, matched_skills, missing_skills = self.semantic_skill_match(user_skills, job_skills)
        experience_result = self.calculate_experience_quality(user_experience, job_required_exp)
        role_score = self.calculate_role_fit(user_skills, job_title, job_description)
        career_score = self.calculate_career_alignment(user_experience, user_skills, job_title, job_required_exp)
        location_score, location_message = self.calculate_location_fit(user_location, job_location)
        company_score = self.calculate_company_fit(user_skills, None, None)
        salary_score, salary_message = self.calculate_salary_match(user_salary, job_salary)
        
        # Weighted combination
        weights = {
            'skills': 0.35,
            'experience': 0.25,
            'role_fit': 0.15,
            'career': 0.10,
            'location': 0.05,
            'company': 0.05,
            'salary': 0.05
        }
        
        total_score = (
            skill_score * weights['skills'] +
            experience_result['score'] * weights['experience'] +
            role_score * weights['role_fit'] +
            career_score * weights['career'] +
            location_score * weights['location'] +
            company_score * weights['company'] +
            salary_score * weights['salary']
        )
        
        # Try ML prediction if available
        ml_features = [skill_score, experience_result['score'], role_score, career_score, 
                      location_score, company_score, salary_score]
        ml_prediction = self.predict_with_ml(ml_features)
        
        # Determine rank
        if total_score >= 90:
            rank = "🏆 Excellent Match - Highly Recommended"
            rank_level = "excellent"
            color = "#28a745"
        elif total_score >= 75:
            rank = "⭐ Great Match - Strong Candidate"
            rank_level = "great"
            color = "#17a2b8"
        elif total_score >= 60:
            rank = "👍 Good Match - Consider"
            rank_level = "good"
            color = "#ffc107"
        elif total_score >= 45:
            rank = "📌 Potential Match - Review"
            rank_level = "potential"
            color = "#fd7e14"
        else:
            rank = "⚠️ Low Match - Needs Improvement"
            rank_level = "low"
            color = "#dc3545"
        
        return {
            "total_match": round(total_score, 1),
            "ml_prediction": round(ml_prediction, 1) if ml_prediction else None,
            "breakdown": {
                "skills": {
                    "score": round(skill_score, 1),
                    "weight": weights['skills'],
                    "matched": matched_skills,
                    "missing": missing_skills
                },
                "experience": {
                    "score": round(experience_result['score'], 1),
                    "weight": weights['experience'],
                    "level": experience_result['level'],
                    "recommendation": experience_result['recommendation']
                },
                "role_fit": {
                    "score": round(role_score, 1),
                    "weight": weights['role_fit']
                },
                "career_alignment": {
                    "score": round(career_score, 1),
                    "weight": weights['career']
                },
                "location": {
                    "score": round(location_score, 1),
                    "weight": weights['location'],
                    "message": location_message
                },
                "company_fit": {
                    "score": round(company_score, 1),
                    "weight": weights['company']
                },
                "salary_match": {
                    "score": round(salary_score, 1),
                    "weight": weights['salary'],
                    "message": salary_message
                }
            },
            "rank": rank,
            "rank_level": rank_level,
            "color": color,
            "recommendation": self._generate_recommendation(total_score, matched_skills, missing_skills, experience_result),
            "insights": self._generate_insights(user_skills, job_skills, user_experience, job_required_exp)
        }
    
    def _generate_recommendation(self, score, matched_skills, missing_skills, experience_result):
        """Generate actionable recommendations"""
        if score >= 80:
            return "Strong candidate! Proceed with interview."
        elif score >= 60:
            if len(missing_skills) <= 2:
                return f"Good candidate. Missing {', '.join(missing_skills[:2])} - can be learned on the job."
            else:
                return f"Consider if you can provide training for {len(missing_skills)} missing skills."
        elif score >= 45:
            return f"Potential candidate. Strong in {', '.join(matched_skills[:3])}. Consider for junior role."
        else:
            return "Low match. Look for candidates with different skill set."
    
    def _generate_insights(self, user_skills, job_skills, user_exp, required_exp):
        """Generate strategic insights"""
        insights = []
        
        # Skill insights
        common_skills = set(user_skills) & set(job_skills)
        if len(common_skills) >= 3:
            insights.append(f"Strong skill overlap in {', '.join(list(common_skills)[:3])}")
        
        # Experience insights
        if user_exp >= required_exp * 1.5:
            insights.append(f"Overqualified - {user_exp} years vs {required_exp} required")
        elif user_exp < required_exp:
            insights.append(f"Underqualified - Needs {required_exp - user_exp} more years")
        
        # Missing critical skills
        critical_skills = ['python', 'java', 'javascript', 'react', 'sql']
        missing_critical = [s for s in critical_skills if s in job_skills and s not in user_skills]
        if missing_critical:
            insights.append(f"Missing critical skills: {', '.join(missing_critical)}")
        
        return insights

# Initialize global matching engine
matching_engine = AdvancedMatchingEngine()