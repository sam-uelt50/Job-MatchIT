import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModel
import torch
import re
from typing import Dict, List, Any, Tuple
from datetime import datetime

class MatchingEngine:
    def __init__(self):
        # Initialize BERT model for semantic matching
        self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        self.model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        self.model.eval()  # Set to evaluation mode
        
        # TF-IDF for keyword matching
        self.tfidf = TfidfVectorizer(max_features=1000, stop_words='english')
        
        # Weights for different components
        self.weights = {
            'skill': 0.40,
            'experience': 0.25,
            'education': 0.15,
            'semantic': 0.20
        }
    
    async def calculate_match(self, resume: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive match between resume and job"""
        
        start_time = datetime.utcnow()
        
        # Calculate individual scores
        skill_match = self._calculate_skill_match(
            resume.get('skills', []),
            resume.get('skill_names', []),
            job.get('required_skills', []),
            job.get('preferred_skills', [])
        )
        
        experience_match = self._calculate_experience_match(
            resume.get('total_experience_years', 0),
            resume.get('experience', []),
            job.get('min_experience_years', 0),
            job.get('experience_level', 'mid')
        )
        
        education_match = self._calculate_education_match(
            resume.get('education', []),
            resume.get('highest_education', ''),
            job.get('education_required', ''),
            job.get('education_preferred', '')
        )
        
        semantic_match = await self._calculate_semantic_similarity(
            self._prepare_text_for_semantic(resume),
            self._prepare_text_for_semantic(job)
        )
        
        # Calculate total score with weights
        total_score = (
            self.weights['skill'] * skill_match['score'] +
            self.weights['experience'] * experience_match['score'] +
            self.weights['education'] * education_match['score'] +
            self.weights['semantic'] * semantic_match['score']
        )
        
        # Determine category
        category = self._get_category(total_score)
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return {
            'total_score': round(total_score, 2),
            'category': category,
            'breakdown': {
                'skill': skill_match,
                'experience': experience_match,
                'education': education_match,
                'semantic': semantic_match
            },
            'matched_skills': skill_match.get('matched_required', []) + skill_match.get('matched_preferred', []),
            'missing_required_skills': skill_match.get('missing_required', []),
            'missing_preferred_skills': skill_match.get('missing_preferred', []),
            'additional_skills': skill_match.get('additional_skills', [])[:10],
            'strengths': self._identify_strengths(skill_match, experience_match, education_match),
            'gaps': self._identify_gaps(skill_match, experience_match, education_match),
            'explanation': self._generate_explanation(total_score, skill_match, experience_match, education_match),
            'processing_time_ms': int(processing_time)
        }
    
    def _calculate_skill_match(self, 
                              candidate_skills: List[Dict],
                              candidate_skill_names: List[str],
                              required_skills: List[str],
                              preferred_skills: List[str]) -> Dict[str, Any]:
        """Calculate skill match score"""
        
        # Normalize to lowercase
        candidate_skills_lower = [s.lower() for s in candidate_skill_names]
        required_lower = [s.lower() for s in required_skills]
        preferred_lower = [s.lower() for s in preferred_skills]
        
        # Find matches
        matched_required = [s for s in required_lower if s in candidate_skills_lower]
        matched_preferred = [s for s in preferred_lower if s in candidate_skills_lower]
        
        # Calculate scores
        required_score = (len(matched_required) / len(required_lower)) * 100 if required_lower else 100
        preferred_score = (len(matched_preferred) / len(preferred_lower)) * 100 if preferred_lower else 100
        
        # Weighted score (required skills count more)
        total_score = (0.7 * required_score + 0.3 * preferred_score)
        
        # Find missing skills
        missing_required = [s for s in required_lower if s not in candidate_skills_lower]
        missing_preferred = [s for s in preferred_lower if s not in candidate_skills_lower]
        
        # Find additional skills (candidate has but job doesn't require)
        additional = [s for s in candidate_skills_lower 
                     if s not in required_lower and s not in preferred_lower]
        
        # Get skill details for important matches
        skill_details = []
        for skill in required_lower[:10]:  # Top 10 required skills
            matched = skill in candidate_skills_lower
            skill_details.append({
                'skill': skill,
                'required': True,
                'matched': matched
            })
        
        return {
            'score': round(total_score, 2),
            'required_score': round(required_score, 2),
            'preferred_score': round(preferred_score, 2),
            'matched_required': matched_required,
            'matched_preferred': matched_preferred,
            'missing_required': missing_required,
            'missing_preferred': missing_preferred,
            'additional_skills': additional[:20],
            'match_percentage': round((len(matched_required) / len(required_lower)) * 100 if required_lower else 100, 2),
            'skill_details': skill_details
        }
    
    def _calculate_experience_match(self,
                                   total_years: float,
                                   experiences: List[Dict],
                                   required_years: float,
                                   required_level: str) -> Dict[str, Any]:
        """Calculate experience match score"""
        
        # Years match
        if total_years >= required_years:
            years_score = 100
        else:
            years_score = (total_years / required_years) * 100 if required_years > 0 else 100
        
        # Level match (entry, mid, senior, lead)
        level_scores = {
            'entry': 1,
            'mid': 2,
            'senior': 3,
            'lead': 4,
            'executive': 5
        }
        
        candidate_level = self._determine_experience_level(total_years)
        required_level_score = level_scores.get(required_level, 2)
        candidate_level_score = level_scores.get(candidate_level, 2)
        
        if candidate_level_score >= required_level_score:
            level_score = 100
        else:
            level_score = (candidate_level_score / required_level_score) * 100
        
        # Role relevance (check if experience is relevant to job)
        relevance_score = self._calculate_role_relevance(experiences, required_level)
        
        # Combined score
        total_score = (0.5 * years_score + 0.3 * level_score + 0.2 * relevance_score)
        
        return {
            'score': round(total_score, 2),
            'years_score': round(years_score, 2),
            'level_score': round(level_score, 2),
            'relevance_score': round(relevance_score, 2),
            'candidate_years': total_years,
            'required_years': required_years,
            'candidate_level': candidate_level,
            'required_level': required_level
        }
    
    def _calculate_education_match(self,
                                  education: List[Dict],
                                  highest_education: str,
                                  required_education: str,
                                  preferred_education: str) -> Dict[str, Any]:
        """Calculate education match score"""
        
        # Education level hierarchy
        level_scores = {
            'phd': 100,
            'master': 90,
            'bachelor': 80,
            'associate': 70,
            'high school': 60,
            'not specified': 50
        }
        
        # Get candidate's highest level
        candidate_level = highest_education.lower() if highest_education else 'not specified'
        candidate_score = level_scores.get(candidate_level, 50)
        
        # Get required level
        required_level = required_education.lower() if required_education else 'not specified'
        required_score = level_scores.get(required_level, 50)
        
        # Calculate level match
        if candidate_score >= required_score:
            level_match_score = 100
        else:
            level_match_score = (candidate_score / required_score) * 100
        
        # Check field match (simplified)
        field_match_score = 100
        if required_education:
            # Check if any education field matches required field
            for edu in education:
                if 'field_of_study' in edu and edu['field_of_study']:
                    if required_education.lower() in edu['field_of_study'].lower():
                        field_match_score = 100
                        break
            else:
                field_match_score = 70  # Partial match
        
        # Combined score
        total_score = (0.7 * level_match_score + 0.3 * field_match_score)
        
        return {
            'score': round(total_score, 2),
            'level_match_score': round(level_match_score, 2),
            'field_match_score': round(field_match_score, 2),
            'candidate_level': highest_education,
            'required_level': required_education,
            'field_match': field_match_score == 100
        }
    
    async def _calculate_semantic_similarity(self, text1: str, text2: str) -> Dict[str, Any]:
        """Calculate semantic similarity using BERT"""
        
        # Tokenize and get embeddings
        inputs1 = self.tokenizer(text1, return_tensors='pt', padding=True, truncation=True, max_length=512)
        inputs2 = self.tokenizer(text2, return_tensors='pt', padding=True, truncation=True, max_length=512)
        
        with torch.no_grad():
            outputs1 = self.model(**inputs1)
            outputs2 = self.model(**inputs2)
            
            # Mean pooling
            embeddings1 = self._mean_pooling(outputs1, inputs1['attention_mask'])
            embeddings2 = self._mean_pooling(outputs2, inputs2['attention_mask'])
            
            # Normalize
            embeddings1 = torch.nn.functional.normalize(embeddings1, p=2, dim=1)
            embeddings2 = torch.nn.functional.normalize(embeddings2, p=2, dim=1)
            
            # Cosine similarity
            similarity = torch.cosine_similarity(embeddings1, embeddings2).item()
        
        # Find key matching phrases (simplified)
        key_phrases = self._extract_key_phrases(text1, text2)
        
        return {
            'score': round(similarity * 100, 2),
            'similarity': similarity,
            'key_phrases': key_phrases
        }
    
    def _mean_pooling(self, model_output, attention_mask):
        """Mean pooling for sentence embeddings"""
        token_embeddings = model_output.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    
    def _prepare_text_for_semantic(self, data: Dict) -> str:
        """Prepare text for semantic similarity"""
        parts = []
        
        # Add job title or relevant info
        if 'title' in data:
            parts.append(f"Job Title: {data['title']}")
        
        # Add skills
        if 'skills' in data:
            if isinstance(data['skills'], list):
                skill_text = " ".join([s.get('name', str(s)) for s in data['skills'][:20]])
                parts.append(f"Skills: {skill_text}")
        
        if 'skill_names' in data:
            parts.append(f"Skills: {' '.join(data['skill_names'][:20])}")
        
        # Add experience descriptions
        if 'experience' in data:
            for exp in data['experience'][:3]:  # Top 3 experiences
                if 'description' in exp:
                    parts.append(exp['description'][:500])
        
        # Add description for jobs
        if 'description' in data:
            parts.append(data['description'][:1000])
        
        # Add requirements
        if 'required_skills' in data:
            parts.append(f"Required: {' '.join(data['required_skills'][:20])}")
        
        return " ".join(parts)[:2000]  # Limit length
    
    def _extract_key_phrases(self, text1: str, text2: str) -> List[str]:
        """Extract key matching phrases (simplified)"""
        # This is a placeholder - in production, use more sophisticated NLP
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        common = words1.intersection(words2)
        
        # Filter common words
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        keywords = [w for w in common if len(w) > 3 and w not in stopwords]
        
        return list(keywords)[:10]
    
    def _determine_experience_level(self, years: float) -> str:
        """Determine experience level based on years"""
        if years < 2:
            return 'entry'
        elif years < 5:
            return 'mid'
        elif years < 8:
            return 'senior'
        else:
            return 'lead'
    
    def _calculate_role_relevance(self, experiences: List[Dict], target_level: str) -> float:
        """Calculate how relevant the experience is to the role"""
        if not experiences:
            return 50
        
        relevance = 70  # Base score
        
        # Check recent roles for seniority
        for exp in experiences[:2]:  # Most recent roles
            if 'title' in exp:
                title = exp['title'].lower()
                if target_level == 'senior' and 'senior' in title:
                    relevance += 15
                elif target_level == 'lead' and ('lead' in title or 'manager' in title):
                    relevance += 15
                elif target_level == 'mid' and ('mid' in title or 'level' in title):
                    relevance += 10
        
        return min(relevance, 100)
    
    def _get_category(self, score: float) -> str:
        """Get candidate category based on score"""
        if score >= 85:
            return "Strong Fit"
        elif score >= 65:
            return "Moderate Fit"
        else:
            return "Weak Fit"
    
    def _identify_strengths(self, skill_match, exp_match, edu_match) -> List[str]:
        """Identify candidate strengths"""
        strengths = []
        
        if skill_match['score'] >= 80:
            strengths.append(f"Strong skill match ({skill_match['match_percentage']}% of required skills)")
        
        if exp_match['score'] >= 80:
            strengths.append(f"Experience level matches or exceeds requirements ({exp_match['candidate_years']} years)")
        
        if edu_match['score'] >= 80:
            strengths.append(f"Educational background meets requirements")
        
        if skill_match.get('additional_skills'):
            strengths.append(f"Has additional relevant skills: {', '.join(skill_match['additional_skills'][:3])}")
        
        return strengths[:5]
    
    def _identify_gaps(self, skill_match, exp_match, edu_match) -> List[str]:
        """Identify candidate gaps"""
        gaps = []
        
        if skill_match['missing_required']:
            missing = skill_match['missing_required'][:3]
            gaps.append(f"Missing required skills: {', '.join(missing)}")
        
        if exp_match['score'] < 60:
            gaps.append(f"Experience below requirements ({exp_match['candidate_years']} years vs {exp_match['required_years']} required)")
        
        if edu_match['score'] < 60:
            gaps.append("Educational background doesn't fully meet requirements")
        
        return gaps[:3]
    
    def _generate_explanation(self, total_score, skill_match, exp_match, edu_match) -> str:
        """Generate human-readable explanation"""
        if total_score >= 85:
            return f"This candidate is a Strong Fit with {total_score}% match. They have strong skill alignment and meet experience requirements."
        elif total_score >= 65:
            main_factor = "skills" if skill_match['score'] > exp_match['score'] else "experience"
            return f"This candidate is a Moderate Fit with {total_score}% match. Their {main_factor} is the main strength, but they have some gaps in { 'required skills' if skill_match['score'] < 70 else 'experience level'}."
        else:
            return f"This candidate is a Weak Fit with {total_score}% match. They are missing key requirements and may not be suitable for this role."