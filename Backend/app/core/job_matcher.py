# app/core/job_matcher.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Tuple
import re

class JobMatcher:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    
    def calculate_skill_match(self, resume_skills: List[str], job_requirements: List[str]) -> float:
        """Calculate skill match percentage"""
        if not job_requirements:
            return 0.0
        
        # Convert lists to strings for matching
        resume_skills_str = ' '.join(resume_skills).lower()
        job_req_str = ' '.join(job_requirements).lower()
        
        matched = 0
        for skill in job_requirements:
            if skill.lower() in resume_skills_str:
                matched += 1
        
        return (matched / len(job_requirements)) * 100
    
    def calculate_experience_match(self, resume_years: int, required_years: int) -> float:
        """Calculate experience match score"""
        if resume_years >= required_years:
            return 100.0
        else:
            return (resume_years / required_years) * 100
    
    def calculate_text_similarity(self, resume_text: str, job_description: str) -> float:
        """Calculate cosine similarity between resume and job description"""
        try:
            # Handle empty text
            if not resume_text or not job_description:
                return 0.0
            
            # Create TF-IDF matrix
            tfidf_matrix = self.vectorizer.fit_transform([resume_text, job_description])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return float(similarity[0][0]) * 100
        except Exception as e:
            print(f"Similarity calculation error: {e}")
            return 0.0
    
    def rank_candidates(self, resume_data: Dict, job_data: Dict) -> Dict:
        """Rank a single candidate against a job"""
        # Extract data with defaults
        resume_skills = resume_data.get('skills', [])
        job_skills = job_data.get('required_skills', [])
        
        resume_experience = resume_data.get('experience_years', 0)
        required_experience = job_data.get('required_experience', 1)
        
        resume_text = resume_data.get('text', '')[:5000]  # Limit text length
        job_description = job_data.get('description', '')
        
        # Calculate individual scores
        skill_match = self.calculate_skill_match(resume_skills, job_skills)
        
        experience_match = self.calculate_experience_match(
            resume_experience,
            required_experience
        )
        
        text_similarity = self.calculate_text_similarity(resume_text, job_description)
        
        # Calculate weighted total score
        weights = {
            'skills': 0.5,      # Skills are most important
            'experience': 0.3,   # Experience next
            'similarity': 0.2    # Overall text similarity
        }
        
        total_score = (
            skill_match * weights['skills'] +
            experience_match * weights['experience'] +
            text_similarity * weights['similarity']
        )
        
        # Determine rank category
        if total_score >= 80:
            rank = "Top Match"
        elif total_score >= 60:
            rank = "Good Match"
        elif total_score >= 40:
            rank = "Potential Match"
        else:
            rank = "Low Match"
        
        return {
            "total_score": round(total_score, 2),
            "skill_match_score": round(skill_match, 2),
            "experience_match_score": round(experience_match, 2),
            "similarity_score": round(text_similarity, 2),
            "rank_category": rank,
            "recommended": total_score >= 60
        }
    
    def rank_multiple_candidates(self, resumes: List[Dict], job_data: Dict) -> List[Dict]:
        """Rank multiple candidates for a single job"""
        ranked = []
        
        for resume in resumes:
            ranking = self.rank_candidates(resume, job_data)
            ranked.append({
                "candidate_id": resume.get('id', 'unknown'),
                "candidate_name": resume.get('name', 'Unknown'),
                "scores": ranking
            })
        
        # Sort by total score (highest first)
        ranked.sort(key=lambda x: x['scores']['total_score'], reverse=True)
        return ranked
    
    def recommend_jobs(self, resume_data: Dict, jobs: List[Dict], top_n: int = 5) -> List[Dict]:
        """Recommend top N jobs for a candidate"""
        recommendations = []
        
        for job in jobs:
            ranking = self.rank_candidates(resume_data, job)
            recommendations.append({
                "job_id": job.get('id', 'unknown'),
                "job_title": job.get('title', 'Unknown'),
                "company": job.get('company', 'Unknown'),
                "match_score": ranking['total_score'],
                "rank_category": ranking['rank_category'],
                "breakdown": {
                    "skills": ranking['skill_match_score'],
                    "experience": ranking['experience_match_score'],
                    "similarity": ranking['similarity_score']
                }
            })
        
        # Sort by match score and return top N
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        return recommendations[:top_n]

# Create singleton instance
job_matcher = JobMatcher()