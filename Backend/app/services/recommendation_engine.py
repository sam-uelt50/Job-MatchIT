import numpy as np
from typing import List, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId

class RecommendationEngine:
    def __init__(self):
        # Weights for different recommendation factors
        self.weights = {
            'content_based': 0.7,
            'collaborative': 0.2,
            'popularity': 0.1
        }
    
    async def get_job_recommendations(self, 
                                      user_id: str,
                                      resume_id: str,
                                      db,
                                      limit: int = 10) -> List[Dict[str, Any]]:
        """Get personalized job recommendations for a candidate"""
        
        # Get user's resume
        resume = await db.resumes.find_one({"_id": ObjectId(resume_id)})
        if not resume:
            return []
        
        # Get all active jobs
        jobs = await db.jobs.find({
            "status": "active",
            "expires_at": {"$gt": datetime.utcnow()}
        }).to_list(length=200)
        
        if not jobs:
            return []
        
        # Calculate content-based scores
        content_scores = await self._content_based_scores(resume, jobs, db)
        
        # Get collaborative scores
        collab_scores = await self._collaborative_scores(user_id, jobs, db)
        
        # Get popularity scores
        popularity_scores = self._popularity_scores(jobs)
        
        # Combine scores
        recommendations = []
        for job in jobs:
            job_id = str(job["_id"])
            
            content_score = content_scores.get(job_id, 0)
            collab_score = collab_scores.get(job_id, 50)  # Default 50
            popularity_score = popularity_scores.get(job_id, 50)
            
            final_score = (
                self.weights['content_based'] * content_score +
                self.weights['collaborative'] * collab_score +
                self.weights['popularity'] * popularity_score
            )
            
            # Check if already applied
            applied = await db.applications.find_one({
                "candidate_id": user_id,
                "job_id": job_id
            })
            
            if not applied:
                # Get match breakdown from content score calculation
                match_breakdown = content_scores.get(f"{job_id}_breakdown", {})
                
                recommendations.append({
                    "job_id": job_id,
                    "job_title": job["title"],
                    "company": job["company"],
                    "location": job.get("location", "Remote"),
                    "match_score": round(final_score, 2),
                    "category": self._get_category(final_score),
                    "breakdown": match_breakdown,
                    "strengths": match_breakdown.get('strengths', [])[:3],
                    "gaps": match_breakdown.get('gaps', [])[:3],
                    "posted_at": job["posted_at"],
                    "expires_at": job["expires_at"]
                })
        
        # Sort by score and return top N
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        return recommendations[:limit]
    
    async def _content_based_scores(self, resume: Dict, jobs: List[Dict], db) -> Dict[str, float]:
        """Calculate content-based recommendation scores"""
        scores = {}
        
        resume_skills = set(resume.get('skill_names', []))
        resume_experience = resume.get('total_experience_years', 0)
        resume_education = resume.get('highest_education', '')
        
        for job in jobs:
            job_id = str(job["_id"])
            
            # Skill match
            required_skills = set(job.get('required_skills', []))
            preferred_skills = set(job.get('preferred_skills', []))
            
            matched_required = resume_skills.intersection(required_skills)
            matched_preferred = resume_skills.intersection(preferred_skills)
            
            skill_score = 0
            if required_skills:
                skill_score = (len(matched_required) / len(required_skills)) * 70
            if preferred_skills:
                skill_score += (len(matched_preferred) / len(preferred_skills)) * 30
            
            # Experience match
            required_years = job.get('min_experience_years', 0)
            if resume_experience >= required_years:
                exp_score = 100
            else:
                exp_score = (resume_experience / required_years) * 100 if required_years > 0 else 100
            
            # Education match (simplified)
            edu_score = 100  # Default
            if 'education_required' in job and job['education_required']:
                # Simple check - would be more sophisticated in production
                edu_score = 80
            
            # Combined score
            total_score = (0.6 * skill_score + 0.3 * exp_score + 0.1 * edu_score)
            
            # Store breakdown
            scores[job_id] = round(total_score, 2)
            scores[f"{job_id}_breakdown"] = {
                'skill_score': round(skill_score, 2),
                'experience_score': round(exp_score, 2),
                'education_score': round(edu_score, 2),
                'matched_skills': list(matched_required)[:10],
                'missing_skills': list(required_skills - resume_skills)[:10],
                'strengths': self._generate_strengths(matched_required, resume_experience, required_years),
                'gaps': self._generate_gaps(required_skills - resume_skills, resume_experience, required_years)
            }
        
        return scores
    
    async def _collaborative_scores(self, user_id: str, jobs: List[Dict], db) -> Dict[str, float]:
        """Calculate collaborative filtering scores"""
        scores = {}
        
        # Get user's application history
        user_apps = await db.applications.find(
            {"candidate_id": user_id}
        ).to_list(length=50)
        
        if not user_apps:
            return scores
        
        # Get jobs user applied to
        applied_job_ids = [app["job_id"] for app in user_apps]
        
        # Find similar users (users who applied to same jobs)
        similar_users = await db.applications.aggregate([
            {"$match": {"job_id": {"$in": applied_job_ids}}},
            {"$group": {"_id": "$candidate_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 50}
        ]).to_list(length=50)
        
        similar_user_ids = [u["_id"] for u in similar_users if u["_id"] != user_id]
        
        if similar_user_ids:
            # Get jobs these similar users applied to
            similar_apps = await db.applications.find(
                {"candidate_id": {"$in": similar_user_ids}}
            ).to_list(length=500)
            
            # Count job popularity among similar users
            job_counts = {}
            for app in similar_apps:
                job_id = app["job_id"]
                if job_id not in applied_job_ids:  # Don't recommend already applied jobs
                    job_counts[job_id] = job_counts.get(job_id, 0) + 1
            
            # Normalize scores
            if job_counts:
                max_count = max(job_counts.values())
                for job_id, count in job_counts.items():
                    scores[job_id] = (count / max_count) * 100
        
        return scores
    
    def _popularity_scores(self, jobs: List[Dict]) -> Dict[str, float]:
        """Calculate popularity-based scores"""
        scores = {}
        
        # Find max applications for normalization
        max_apps = max([j.get('applications_count', 0) for j in jobs]) if jobs else 1
        
        for job in jobs:
            job_id = str(job["_id"])
            app_count = job.get('applications_count', 0)
            
            if max_apps > 0:
                scores[job_id] = (app_count / max_apps) * 100
            else:
                scores[job_id] = 50  # Default
        
        return scores
    
    def _generate_strengths(self, matched_skills, resume_experience, required_years) -> List[str]:
        """Generate strengths based on match"""
        strengths = []
        
        if matched_skills:
            strengths.append(f"Matched {len(matched_skills)} required skills")
        
        if resume_experience >= required_years:
            strengths.append(f"Experience meets requirement ({resume_experience} years)")
        
        return strengths
    
    def _generate_gaps(self, missing_skills, resume_experience, required_years) -> List[str]:
        """Generate gaps based on match"""
        gaps = []
        
        if missing_skills:
            missing_list = list(missing_skills)[:3]
            strengths.append(f"Missing skills: {', '.join(missing_list)}")
        
        if resume_experience < required_years:
            strengths.append(f"Experience gap: {required_years - resume_experience} years")
        
        return gaps
    
    def _get_category(self, score: float) -> str:
        """Get category based on score"""
        if score >= 80:
            return "Excellent Match"
        elif score >= 65:
            return "Good Match"
        elif score >= 50:
            return "Potential Match"
        else:
            return "Consider Later"