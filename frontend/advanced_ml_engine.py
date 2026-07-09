# -*- coding: utf-8 -*-
"""
ADVANCED ML ENGINE FOR JOBMATCH ET
Analyzes every detail: Skills, Experience, Education, Location, Salary, Cultural Fit
"""

import pickle
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime
import json

class AdvancedMLEngine:
    def __init__(self):
        self.char_vectorizer = None
        self.char_vectors = None
        self.word_vectorizer = None
        self.word_vectors = None
        self.job_titles = None
        self.load_models()
        
        # Skill categories and weights
        self.skill_categories = {
            'programming_languages': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin'],
            'frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'node', 'express', 'rails', 'laravel'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'firebase', 'dynamodb'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 'gitlab'],
            'soft_skills': ['leadership', 'communication', 'teamwork', 'problem solving', 'critical thinking', 'time management'],
            'design': ['figma', 'adobe xd', 'photoshop', 'illustrator', 'ui design', 'ux research'],
            'data_science': ['machine learning', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn', 'nlp'],
            'business': ['project management', 'agile', 'scrum', 'sales', 'marketing', 'finance', 'accounting']
        }
        
        # Education level weights
        self.edu_weights = {
            'phd': 100,
            'master': 90,
            'bachelor': 75,
            'degree': 70,
            'diploma': 50,
            'certificate': 35,
            'high school': 20,
            'none': 0
        }
        
        # Industry sectors
        self.industries = ['Technology', 'Healthcare', 'Finance', 'Education', 'Agriculture', 'Manufacturing', 'Construction', 'Telecom', 'Hospitality']
    
    def load_models(self):
        try:
            self.char_vectorizer = pickle.load(open('ethiopian_job_vectorizer_char.pkl', 'rb'))
            self.char_vectors = pickle.load(open('ethiopian_job_vectors_char.pkl', 'rb'))
            self.word_vectorizer = pickle.load(open('ethiopian_job_vectorizer_word.pkl', 'rb'))
            self.word_vectors = pickle.load(open('ethiopian_job_vectors_word.pkl', 'rb'))
            self.job_titles = pickle.load(open('ethiopian_job_titles.pkl', 'rb'))
            print(f"✅ Advanced ML Engine loaded: {len(self.job_titles):,} titles")
            return True
        except Exception as e:
            print(f"⚠️ Error loading models: {e}")
            return False
    
    def analyze_candidate_complete(self, candidate):
        """
        Complete candidate analysis - extracts everything from profile
        """
        analysis = {
            'skills_analysis': self._analyze_skills(candidate.get('skills', [])),
            'experience_analysis': self._analyze_experience(candidate.get('experience_years', 0), candidate.get('experience_description', '')),
            'education_analysis': self._analyze_education(candidate.get('education_details', [])),
            'location_analysis': self._analyze_location(candidate.get('location', ''), candidate.get('region', '')),
            'salary_analysis': self._analyze_salary(candidate.get('expected_salary', 0)),
            'summary_analysis': self._analyze_summary(candidate.get('professional_summary', '')),
            'project_analysis': self._analyze_projects(candidate.get('projects', [])),
            'language_analysis': self._analyze_languages(candidate.get('languages', [])),
            'certification_analysis': self._analyze_certifications(candidate.get('certifications', []))
        }
        
        # Calculate overall profile score
        analysis['profile_score'] = self._calculate_profile_score(analysis)
        analysis['strengths'] = self._identify_strengths(analysis)
        analysis['weaknesses'] = self._identify_weaknesses(analysis)
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _analyze_skills(self, skills):
        """Deep skill analysis with categorization"""
        if not skills:
            return {'total': 0, 'categories': {}, 'top_skills': [], 'skill_level': 'beginner'}
        
        skills_lower = [s.lower() for s in skills]
        categorized = {cat: [] for cat in self.skill_categories.keys()}
        uncategorized = []
        
        for skill in skills_lower:
            categorized_flag = False
            for cat, keywords in self.skill_categories.items():
                if skill in keywords:
                    categorized[cat].append(skill)
                    categorized_flag = True
                    break
            if not categorized_flag:
                uncategorized.append(skill)
        
        # Calculate skill level based on number and diversity
        total_skills = len(skills)
        categories_count = sum(1 for cat_skills in categorized.values() if cat_skills)
        
        if total_skills >= 15 and categories_count >= 4:
            skill_level = 'expert'
        elif total_skills >= 8 and categories_count >= 2:
            skill_level = 'intermediate'
        elif total_skills >= 3:
            skill_level = 'beginner'
        else:
            skill_level = 'novice'
        
        return {
            'total': total_skills,
            'categories': {cat: len(skills) for cat, skills in categorized.items()},
            'categorized_skills': categorized,
            'uncategorized': uncategorized,
            'skill_level': skill_level,
            'top_skills': skills[:5]
        }
    
    def _analyze_experience(self, years, description):
        """Analyze experience quality and relevance"""
        if years == 0:
            return {'years': 0, 'level': 'entry', 'quality_score': 0, 'insights': ['No experience recorded']}
        
        # Determine level
        if years >= 8:
            level = 'senior'
        elif years >= 5:
            level = 'mid_senior'
        elif years >= 3:
            level = 'mid'
        elif years >= 1:
            level = 'junior'
        else:
            level = 'entry'
        
        # Analyze description quality
        quality_score = 50
        insights = []
        
        if description:
            desc_lower = description.lower()
            word_count = len(description.split())
            
            if word_count > 100:
                quality_score += 25
                insights.append('✅ Detailed experience description')
            elif word_count > 50:
                quality_score += 15
                insights.append('📝 Good experience description')
            
            # Check for keywords
            leadership_keywords = ['lead', 'manage', 'supervise', 'direct', 'head']
            if any(kw in desc_lower for kw in leadership_keywords):
                quality_score += 10
                insights.append('👔 Leadership experience detected')
            
            achievement_keywords = ['increased', 'improved', 'reduced', 'saved', 'achieved', 'award']
            if any(kw in desc_lower for kw in achievement_keywords):
                quality_score += 10
                insights.append('🏆 Achievements mentioned')
        else:
            insights.append('⚠️ Add detailed experience description for better matches')
        
        return {
            'years': years,
            'level': level,
            'quality_score': min(100, quality_score),
            'insights': insights
        }
    
    def _analyze_education(self, education_details):
        """Analyze education background"""
        if not education_details:
            return {'highest_degree': 'none', 'score': 0, 'field': '', 'insights': ['No education recorded']}
        
        highest_score = 0
        highest_degree = ''
        fields = []
        
        for edu in education_details:
            degree = edu.get('degree', '').lower()
            field = edu.get('field_of_study', '')
            gpa = edu.get('gpa', 0)
            specialization = edu.get('specialization', '')
            
            # Get degree score
            degree_score = 0
            for d, score in self.edu_weights.items():
                if d in degree:
                    degree_score = score
                    break
            
            if degree_score > highest_score:
                highest_score = degree_score
                highest_degree = degree
            
            if field:
                fields.append(field)
            
            # GPA bonus
            if gpa >= 3.5:
                highest_score += 10
            elif gpa >= 3.0:
                highest_score += 5
            
            if specialization:
                highest_score += 5
        
        # Determine level
        if highest_score >= 90:
            level = 'expert'
        elif highest_score >= 75:
            level = 'advanced'
        elif highest_score >= 50:
            level = 'intermediate'
        elif highest_score > 0:
            level = 'basic'
        else:
            level = 'none'
        
        insights = []
        if highest_degree:
            insights.append(f'🎓 Highest: {highest_degree.title()}')
        if fields:
            insights.append(f'📚 Fields: {", ".join(fields[:2])}')
        
        return {
            'highest_degree': highest_degree,
            'score': min(100, highest_score),
            'level': level,
            'fields': fields,
            'insights': insights
        }
    
    def _analyze_location(self, location, region):
        """Analyze location preferences"""
        if not location:
            return {'has_location': False, 'score': 0}
        
        location_lower = location.lower()
        
        # Ethiopian regions priority
        high_demand_regions = ['addis ababa', 'oromia', 'amhara', 'tigray', 'dire dawa']
        
        is_high_demand = any(region.lower() in location_lower for region in high_demand_regions)
        is_remote = 'remote' in location_lower or 'anywhere' in location_lower
        
        score = 100 if is_high_demand else (70 if is_remote else 50)
        
        return {
            'has_location': True,
            'location': location,
            'region': region,
            'is_high_demand': is_high_demand,
            'is_remote': is_remote,
            'score': score
        }
    
    def _analyze_salary(self, expected_salary):
        """Analyze salary expectations"""
        if expected_salary == 0:
            return {'has_salary': False, 'score': 50, 'insights': ['Salary expectation not set']}
        
        # Ethiopian salary bands (ETB/month)
        if expected_salary < 5000:
            band = 'entry'
            score = 100
        elif expected_salary < 15000:
            band = 'junior'
            score = 90
        elif expected_salary < 30000:
            band = 'mid'
            score = 80
        elif expected_salary < 50000:
            band = 'senior'
            score = 70
        else:
            band = 'executive'
            score = 60
        
        return {
            'has_salary': True,
            'expected': expected_salary,
            'band': band,
            'score': score,
            'insights': [f'💰 Expects {band} level salary']
        }
    
    def _analyze_summary(self, summary):
        """NLP analysis of professional summary"""
        if not summary:
            return {'has_summary': False, 'score': 0, 'word_count': 0, 'insights': ['Add professional summary']}
        
        word_count = len(summary.split())
        
        # Score based on length and content
        score = 50
        insights = []
        
        if word_count >= 150:
            score += 30
            insights.append('✅ Excellent detail in summary')
        elif word_count >= 75:
            score += 20
            insights.append('📝 Good summary length')
        elif word_count >= 30:
            score += 10
            insights.append('✏️ Consider adding more detail')
        else:
            insights.append('⚠️ Very brief summary - add more detail')
        
        # Check for keywords
        summary_lower = summary.lower()
        keywords_found = []
        
        for cat, keywords in self.skill_categories.items():
            for kw in keywords:
                if kw in summary_lower:
                    keywords_found.append(kw)
        
        if keywords_found:
            score += min(20, len(keywords_found))
            insights.append(f'🔑 Key terms found: {", ".join(keywords_found[:3])}')
        
        return {
            'has_summary': True,
            'word_count': word_count,
            'score': min(100, score),
            'keywords_found': keywords_found[:10],
            'insights': insights
        }
    
    def _analyze_projects(self, projects):
        """Analyze project portfolio"""
        if not projects:
            return {'count': 0, 'score': 0, 'insights': ['No projects added']}
        
        score = min(50, len(projects) * 10)
        insights = []
        
        if len(projects) >= 3:
            score += 20
            insights.append(f'✅ {len(projects)} projects - strong portfolio')
        elif len(projects) >= 1:
            score += 10
            insights.append(f'📁 {len(projects)} project(s) in portfolio')
        
        # Check for project descriptions
        has_descriptions = any(p.get('description') for p in projects)
        if has_descriptions:
            score += 15
            insights.append('📝 Projects have detailed descriptions')
        
        return {
            'count': len(projects),
            'score': min(100, score),
            'has_descriptions': has_descriptions,
            'insights': insights
        }
    
    def _analyze_languages(self, languages):
        """Analyze language skills"""
        if not languages:
            return {'count': 0, 'score': 0}
        
        score = min(50, len(languages) * 15)
        
        # Bonus for English proficiency
        for lang in languages:
            if 'english' in lang.get('name', '').lower():
                proficiency = lang.get('proficiency', '').lower()
                if proficiency == 'native' or proficiency == 'fluent':
                    score += 30
                elif proficiency == 'advanced':
                    score += 20
        
        return {
            'count': len(languages),
            'score': min(100, score)
        }
    
    def _analyze_certifications(self, certifications):
        """Analyze certifications"""
        if not certifications:
            return {'count': 0, 'score': 0}
        
        score = min(50, len(certifications) * 15)
        
        return {
            'count': len(certifications),
            'score': min(100, score)
        }
    
    def _calculate_profile_score(self, analysis):
        """Calculate overall profile completeness score"""
        weights = {
            'skills_analysis': 0.25,
            'experience_analysis': 0.20,
            'education_analysis': 0.15,
            'summary_analysis': 0.15,
            'project_analysis': 0.10,
            'location_analysis': 0.05,
            'salary_analysis': 0.05,
            'language_analysis': 0.03,
            'certification_analysis': 0.02
        }
        
        total = 0
        for key, weight in weights.items():
            if key in analysis:
                score = analysis[key].get('score', 0)
                total += score * weight
        
        return round(total, 1)
    
    def _identify_strengths(self, analysis):
        """Identify candidate strengths"""
        strengths = []
        
        if analysis['skills_analysis']['total'] >= 10:
            strengths.append(f"Strong technical skills ({analysis['skills_analysis']['total']} skills)")
        
        if analysis['experience_analysis']['years'] >= 5:
            strengths.append(f"Solid experience ({analysis['experience_analysis']['years']} years)")
        
        if analysis['education_analysis']['score'] >= 70:
            strengths.append("Good educational background")
        
        if analysis['project_analysis']['count'] >= 3:
            strengths.append("Strong project portfolio")
        
        if analysis['summary_analysis']['score'] >= 70:
            strengths.append("Excellent professional summary")
        
        return strengths[:5]
    
    def _identify_weaknesses(self, analysis):
        """Identify areas for improvement"""
        weaknesses = []
        
        if analysis['skills_analysis']['total'] < 5:
            weaknesses.append("Add more technical skills")
        
        if analysis['experience_analysis']['years'] < 2:
            weaknesses.append("Limited work experience")
        
        if analysis['education_analysis']['score'] < 50:
            weaknesses.append("Add education details")
        
        if analysis['summary_analysis']['score'] < 50:
            weaknesses.append("Improve professional summary")
        
        if analysis['project_analysis']['count'] == 0:
            weaknesses.append("Add projects to showcase work")
        
        return weaknesses[:5]
    
    def _generate_recommendations(self, analysis):
        """Generate personalized recommendations"""
        recommendations = []
        
        # Skill recommendations
        if analysis['skills_analysis']['total'] < 8:
            recommendations.append("💡 Add more skills to increase match chances")
        
        # Category-specific recommendations
        categories = analysis['skills_analysis']['categories']
        if categories.get('programming_languages', 0) < 2:
            recommendations.append("💻 Learn a programming language (Python, JavaScript, Java)")
        
        if categories.get('cloud', 0) == 0 and categories.get('frameworks', 0) == 0:
            recommendations.append("☁️ Consider learning cloud technologies (AWS, Docker)")
        
        if categories.get('soft_skills', 0) < 2:
            recommendations.append("🤝 Highlight soft skills (Leadership, Communication)")
        
        # Summary recommendation
        if analysis['summary_analysis']['word_count'] < 75:
            recommendations.append("📝 Write a detailed professional summary")
        
        # Project recommendation
        if analysis['project_analysis']['count'] < 2:
            recommendations.append("🚀 Add personal projects to demonstrate skills")
        
        return recommendations[:5]
    
    def calculate_job_match(self, candidate_analysis, job):
        """
        Calculate match between candidate and job with detailed scoring
        """
        job_skills = job.get('required_skills', [])
        job_skills_lower = [s.lower() for s in job_skills]
        
        # 1. SKILLS MATCH (40%)
        candidate_skills = candidate_analysis['skills_analysis']['categorized_skills']
        all_candidate_skills = []
        for cat_skills in candidate_skills.values():
            all_candidate_skills.extend(cat_skills)
        
        matched = 0
        for js in job_skills_lower:
            if js in all_candidate_skills:
                matched += 1
            else:
                # Check partial matches
                for cs in all_candidate_skills:
                    if js in cs or cs in js:
                        matched += 0.5
                        break
        
        skills_match = (matched / max(1, len(job_skills))) * 100
        
        # 2. EXPERIENCE MATCH (25%)
        required_exp = job.get('experience_required', 2)
        candidate_exp = candidate_analysis['experience_analysis']['years']
        exp_match = 100 if candidate_exp >= required_exp else (candidate_exp / required_exp) * 100
        
        # 3. EDUCATION MATCH (15%)
        required_edu = job.get('required_education', '').lower()
        candidate_edu_score = candidate_analysis['education_analysis']['score']
        
        if not required_edu:
            edu_match = 100
        else:
            required_score = 0
            for degree, score in self.edu_weights.items():
                if degree in required_edu:
                    required_score = score
                    break
            edu_match = min(100, (candidate_edu_score / max(1, required_score)) * 100) if required_score > 0 else 70
        
        # 4. LOCATION MATCH (10%)
        candidate_location = candidate_analysis['location_analysis']
        job_location = job.get('location', '')
        
        if candidate_location.get('is_remote', False) or 'remote' in job_location.lower():
            location_match = 100
        elif candidate_location.get('location', '') and job_location:
            location_match = 80 if candidate_location['location'].lower() in job_location.lower() else 50
        else:
            location_match = 70
        
        # 5. SALARY MATCH (5%)
        candidate_salary = candidate_analysis['salary_analysis'].get('expected', 0)
        job_salary_range = job.get('salary_range', '')
        
        if candidate_salary == 0:
            salary_match = 70
        else:
            # Extract salary from range
            import re
            numbers = re.findall(r'\d+', job_salary_range)
            if numbers:
                avg_salary = sum(map(int, numbers[:2])) / 2
                if candidate_salary <= avg_salary * 1.2:
                    salary_match = 100
                elif candidate_salary <= avg_salary * 1.5:
                    salary_match = 70
                else:
                    salary_match = 50
            else:
                salary_match = 70
        
        # 6. JOB TITLE SIMILARITY (5%)
        job_title = job.get('title', '')
        title_match = 50
        if job_title and self.job_titles:
            try:
                test_vec = self.char_vectorizer.transform([job_title.lower()])
                similarities = cosine_similarity(test_vec, self.char_vectors)[0]
                title_match = np.mean(similarities) * 100
            except:
                pass
        
        # Calculate final score
        final_score = (
            (skills_match * 0.40) +
            (exp_match * 0.25) +
            (edu_match * 0.15) +
            (location_match * 0.10) +
            (salary_match * 0.05) +
            (title_match * 0.05)
        )
        
        final_score = min(100, max(0, round(final_score)))
        
        # Generate match explanations
        explanations = []
        
        if skills_match >= 80:
            explanations.append(f"✅ Strong skills match ({skills_match:.0f}%)")
        elif skills_match >= 60:
            explanations.append(f"📚 Good skills match ({skills_match:.0f}%)")
        else:
            explanations.append(f"⚠️ Skills gap ({skills_match:.0f}%) - consider developing: {', '.join(job_skills[:3])}")
        
        if exp_match >= 80:
            explanations.append(f"⏰ Experience matches ({candidate_exp} years)")
        else:
            needed = required_exp - candidate_exp
            explanations.append(f"📅 Need {needed} more years of experience")
        
        if edu_match >= 80:
            explanations.append(f"🎓 Education background is relevant")
        
        if location_match >= 80:
            explanations.append(f"📍 Location compatible")
        
        return {
            'total_score': final_score,
            'skills_match': round(skills_match, 1),
            'experience_match': round(exp_match, 1),
            'education_match': round(edu_match, 1),
            'location_match': round(location_match, 1),
            'salary_match': round(salary_match, 1),
            'title_match': round(title_match, 1),
            'explanations': explanations,
            'level': self._get_match_level(final_score),
            'color': self._get_match_color(final_score)
        }
    
    def _get_match_level(self, score):
        if score >= 85:
            return "🏆 Excellent Match"
        elif score >= 70:
            return "⭐ Great Match"
        elif score >= 55:
            return "👍 Good Match"
        elif score >= 40:
            return "📌 Potential Match"
        else:
            return "⚠️ Low Match"
    
    def _get_match_color(self, score):
        if score >= 85:
            return "#28a745"
        elif score >= 70:
            return "#17a2b8"
        elif score >= 55:
            return "#ffc107"
        elif score >= 40:
            return "#fd7e14"
        else:
            return "#dc3545"

# Initialize global engine
ml_engine = AdvancedMLEngine()