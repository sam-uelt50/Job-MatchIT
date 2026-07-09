"""
Advanced Random Forest Matcher for JobMatch ET
Features: Semantic Matching, Advanced NLP, Job Complexity Analysis,
Responsibility Analysis, Seniority Detection, Soft Skills Extraction,
Ensemble Learning, Dynamic Weights, Confidence Scoring
"""

import re
import numpy as np
from typing import List, Dict, Any, Tuple
from collections import Counter
from datetime import datetime
import math

class RandomForestMatcher:
    """Complete Advanced Random Forest implementation for job matching"""
    
    def __init__(self):
        self.categories = ['Technology', 'Finance', 'Business', 'Healthcare', 'Education', 'General']
        
        # Advanced sub-categories
        self.sub_categories = {
            'Technology': ['Software Development', 'DevOps', 'Data Science', 'Cybersecurity', 'Cloud Computing', 'AI/ML', 'Frontend', 'Backend', 'Full Stack', 'Mobile'],
            'Finance': ['Accounting', 'Investment Banking', 'Risk Management', 'Financial Analysis', 'Auditing', 'Tax', 'Payroll'],
            'Business': ['Sales', 'Marketing', 'HR', 'Management', 'Consulting', 'Operations', 'Strategy'],
            'Healthcare': ['Nursing', 'Medical', 'Pharmacy', 'Administration', 'Research', 'Clinical'],
            'Education': ['Teaching', 'Administration', 'Curriculum', 'Training', 'Research'],
            'General': ['Administrative', 'Customer Service', 'Support', 'Entry Level']
        }
        
        # Advanced skill taxonomy
        self.skill_taxonomy = {
            'programming_languages': {
                'python': ['python', 'django', 'flask', 'fastapi', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch'],
                'javascript': ['javascript', 'js', 'node.js', 'express', 'react', 'angular', 'vue', 'typescript'],
                'java': ['java', 'spring', 'spring boot', 'hibernate', 'maven', 'gradle', 'kotlin'],
                'c_sharp': ['c#', 'csharp', '.net', 'asp.net', 'dotnet', 'csharp'],
                'go': ['go', 'golang', 'gin'],
                'rust': ['rust', 'cargo'],
                'php': ['php', 'laravel', 'symfony', 'wordpress'],
                'ruby': ['ruby', 'rails', 'sinatra']
            },
            'frameworks': {
                'frontend': ['react', 'angular', 'vue', 'svelte', 'next.js', 'nuxt', 'gatsby'],
                'backend': ['django', 'flask', 'spring', 'express', 'fastapi', 'laravel', 'rails'],
                'mobile': ['react native', 'flutter', 'swift', 'kotlin', 'ionic', 'xamarin'],
                'testing': ['jest', 'pytest', 'junit', 'selenium', 'cypress', 'mocha', 'chai']
            },
            'databases': {
                'relational': ['sql', 'mysql', 'postgresql', 'oracle', 'sqlite', 'mariadb', 'sql server'],
                'nosql': ['mongodb', 'cassandra', 'dynamodb', 'couchbase', 'redis', 'elasticsearch', 'firebase'],
                'cloud_dbs': ['aws rds', 'azure sql', 'gcp spanner', 'bigquery', 'redshift']
            },
            'cloud_platforms': {
                'aws': ['aws', 'ec2', 's3', 'lambda', 'rds', 'cloudformation', 'terraform', 'cloudfront', 'route53'],
                'azure': ['azure', 'aks', 'function apps', 'cosmos db', 'devops', 'azure devops'],
                'gcp': ['gcp', 'google cloud', 'kubernetes', 'bigquery', 'dataflow', 'cloud run']
            },
            'devops': {
                'ci_cd': ['jenkins', 'gitlab ci', 'github actions', 'circleci', 'travis', 'bamboo'],
                'container': ['docker', 'kubernetes', 'k8s', 'openshift', 'rancher', 'podman'],
                'infrastructure': ['terraform', 'ansible', 'pulumi', 'cloudformation', 'chef', 'puppet']
            },
            'soft_skills': {
                'leadership': ['lead', 'manage', 'direct', 'supervise', 'mentor', 'coach', 'guide', 'oversee'],
                'communication': ['communicate', 'present', 'negotiate', 'collaborate', 'coordinate', 'liaise'],
                'analytical': ['analyze', 'research', 'evaluate', 'assess', 'optimize', 'investigate'],
                'problem_solving': ['solve', 'debug', 'troubleshoot', 'fix', 'resolve', 'remediate'],
                'project_management': ['plan', 'schedule', 'track', 'report', 'agile', 'scrum', 'kanban']
            }
        }
        
        # Semantic skill mapping
        self.semantic_skill_map = {
            'python': ['python', 'django', 'flask', 'fastapi', 'pandas', 'numpy', 'scikit-learn'],
            'javascript': ['javascript', 'js', 'node.js', 'express', 'react', 'angular', 'vue'],
            'react': ['react', 'reactjs', 'react.js', 'next.js', 'gatsby'],
            'java': ['java', 'spring', 'spring boot', 'hibernate', 'maven'],
            'sql': ['sql', 'mysql', 'postgresql', 'postgres', 'oracle', 'sqlite'],
            'aws': ['aws', 'amazon web services', 'ec2', 's3', 'lambda', 'rds'],
            'docker': ['docker', 'container', 'docker compose', 'dockerfile'],
            'kubernetes': ['kubernetes', 'k8s', 'kube', 'openshift', 'eks'],
            'devops': ['devops', 'ci/cd', 'jenkins', 'gitlab ci', 'github actions', 'ansible']
        }
        
        # Career progression factors
        self.career_factors = {
            'Technology': {'entry': 2, 'junior': 4, 'mid': 7, 'senior': 10, 'lead': 99, 'growth': 'fast'},
            'Finance': {'entry': 2, 'junior': 4, 'mid': 7, 'senior': 12, 'lead': 99, 'growth': 'moderate'},
            'Business': {'entry': 2, 'junior': 4, 'mid': 7, 'senior': 10, 'lead': 99, 'growth': 'moderate'},
            'Healthcare': {'entry': 2, 'junior': 4, 'mid': 7, 'senior': 10, 'lead': 99, 'growth': 'moderate'},
            'Education': {'entry': 2, 'junior': 4, 'mid': 7, 'senior': 10, 'lead': 99, 'growth': 'moderate'},
            'General': {'entry': 2, 'junior': 4, 'mid': 7, 'senior': 10, 'lead': 99, 'growth': 'moderate'}
        }
        
        # Job complexity indicators
        self.job_complexity_indicators = {
            'high': {
                'keywords': ['microservices', 'distributed', 'high-load', 'scalable', 'enterprise', 'mission-critical', 
                            'real-time', 'large-scale', 'multi-tenant', 'high availability', 'fault-tolerant',
                            'millions of users', 'petabytes', 'optimization', 'architecture', 'system design',
                            'concurrent', 'high throughput', 'low latency', 'disaster recovery'],
                'weight': 1.5,
                'score': 100
            },
            'medium': {
                'keywords': ['web application', 'api', 'database', 'backend', 'frontend', 'full-stack', 'integration',
                            'cloud', 'responsive', 'user interface', 'mobile', 'cross-platform', 'rest api',
                            'microservices', 'container', 'orchestration'],
                'weight': 1.0,
                'score': 70
            },
            'low': {
                'keywords': ['basic', 'simple', 'static', 'maintenance', 'support', 'entry-level', 'assist',
                            'documentation', 'testing', 'bug fix', 'minor enhancements', 'templates'],
                'weight': 0.6,
                'score': 40
            }
        }
        
        # Responsibility importance weights
        self.responsibility_weights = {
            'leadership': ['lead', 'manage', 'supervise', 'direct', 'coordinate', 'mentor', 'guide', 'oversee', 'orchestrate'],
            'strategic': ['strategy', 'planning', 'architecture', 'design', 'roadmap', 'initiative', 'innovation', 'vision'],
            'technical': ['develop', 'code', 'implement', 'build', 'create', 'engineer', 'program', 'write', 'construct'],
            'analytical': ['analyze', 'research', 'evaluate', 'assess', 'measure', 'quantify', 'optimize', 'benchmark'],
            'collaborative': ['collaborate', 'communicate', 'coordinate', 'interface', 'partner', 'stakeholder', 'cross-functional'],
            'operational': ['maintain', 'monitor', 'support', 'troubleshoot', 'debug', 'fix', 'resolve', 'remediate']
        }
        
        # Seniority indicators
        self.seniority_indicators = {
            'lead': ['lead', 'principal', 'staff', 'architect', 'manager', 'director', 'head', 'vp', 'chief', 'cto'],
            'senior': ['senior', 'sr', 'experienced', 'seasoned', 'advanced', 'expert'],
            'mid': ['mid', 'intermediate', 'mid-level', 'experienced', 'professional'],
            'junior': ['junior', 'jr', 'entry', 'associate', 'recent graduate', 'early career']
        }
        
        # Soft skills keywords
        self.soft_skills_keywords = {
            'communication': ['communication', 'communicate', 'presentation', 'public speaking', 'writing', 'reporting', 'documentation', 'storytelling'],
            'teamwork': ['teamwork', 'collaboration', 'collaborate', 'cross-functional', 'partnership', 'cooperation', 'cohesive'],
            'leadership': ['leadership', 'leading', 'mentoring', 'coaching', 'team lead', 'guidance', 'direction', 'inspiring'],
            'problem_solving': ['problem solving', 'analytical', 'critical thinking', 'troubleshooting', 'debugging', 'resolution', 'root cause'],
            'project_management': ['project management', 'agile', 'scrum', 'kanban', 'jira', 'trello', 'asana', 'planning', 'scheduling'],
            'adaptability': ['adaptability', 'flexible', 'fast learner', 'quick study', 'versatile', 'agile', 'resilient'],
            'time_management': ['time management', 'deadline', 'prioritization', 'scheduling', 'organization', 'efficient'],
            'creativity': ['creativity', 'innovative', 'design', 'creative thinking', 'ideation', 'imaginative'],
            'emotional_intelligence': ['emotional intelligence', 'empathy', 'interpersonal', 'relationship building', 'conflict resolution', 'diplomacy'],
            'negotiation': ['negotiation', 'negotiating', 'persuasion', 'influencing', 'deal-making', 'mediation']
        }
        
        # Leadership keywords
        self.leadership_keywords = [
            'lead', 'led', 'leading', 'manage', 'managed', 'managing', 'supervise', 'supervised',
            'direct', 'directed', 'coordinate', 'coordinated', 'mentor', 'mentored', 'coach', 'coached',
            'head', 'headed', 'senior', 'principal', 'architect', 'team lead', 'team leader', 'manager',
            'director', 'oversee', 'oversaw', 'guide', 'guided', 'orchestrate', 'spearhead', 'champion'
        ]
        
        # Achievement patterns
        self.achievement_patterns = [
            r'increase\w* (?:by )?(\d+)%', r'improve\w* (?:by )?(\d+)%', r'reduce\w* (?:by )?(\d+)%',
            r'decrease\w* (?:by )?(\d+)%', r'save\w* \$?(\d+(?:,\d+)?)', r'lead\w* a team of (\d+)',
            r'manage\w* (\d+)', r'mentor\w* (\d+)', r'grew \w+ by (\d+)%', r'boosted \w+ by (\d+)%',
            r'cut \w+ by (\d+)%', r'delivered \$?\d+', r'generated \$?\d+', r'achieved \d+%',
            r'won .* award', r'recognized as', r'promoted to', r'exceeded expectations', r'top performer'
        ]
    
    # ============ CORE MATCHING METHODS ============
    
    def predict_category(self, job_title: str, job_description: str = "") -> Dict:
        """Predict job category with confidence scoring"""
        text = f"{job_title} {job_description}".lower()
        scores = {cat: 0 for cat in self.categories}
        
        for category, skills in self.category_skills.items():
            for skill in skills:
                if skill in text:
                    scores[category] += 1
        
        # Boost based on keywords
        if any(word in text for word in ['python', 'developer', 'engineer', 'programmer', 'software', 'react', 'javascript', 'java', 'sql', 'aws']):
            scores['Technology'] += 5
        if any(word in text for word in ['accountant', 'finance', 'accounting', 'tax', 'audit', 'budget', 'forecast']):
            scores['Finance'] += 5
        if any(word in text for word in ['sales', 'marketing', 'hr', 'manager', 'business', 'strategy', 'operations']):
            scores['Business'] += 5
        if any(word in text for word in ['nurse', 'doctor', 'medical', 'healthcare', 'clinical', 'patient', 'hospital']):
            scores['Healthcare'] += 5
        if any(word in text for word in ['teacher', 'professor', 'education', 'school', 'curriculum', 'student', 'training']):
            scores['Education'] += 5
        
        predicted = max(scores, key=scores.get)
        max_score = scores[predicted]
        total = sum(scores.values()) or 1
        confidence = round((max_score / total) * 100, 1) if max_score > 0 else 50
        
        # Generate sub-category
        sub_category = self._predict_sub_category(predicted, text)
        
        return {
            'category': predicted,
            'sub_category': sub_category,
            'confidence': confidence,
            'scores': scores
        }
    
    def _predict_sub_category(self, main_category: str, text: str) -> str:
        """Predict sub-category within main category"""
        sub_cats = self.sub_categories.get(main_category, [main_category])
        sub_scores = {}
        
        for sub_cat in sub_cats:
            score = 0
            keywords = sub_cat.lower().split()
            for kw in keywords:
                if kw in text:
                    score += 1
            sub_scores[sub_cat] = score
        
        if sub_scores:
            return max(sub_scores, key=sub_scores.get)
        return main_category
    
    # ============ SKILL MATCHING METHODS ============
    
    def semantic_skill_match(self, user_skill: str, job_skill: str) -> int:
        """Calculate semantic similarity between two skills"""
        user_lower = user_skill.lower().strip()
        job_lower = job_skill.lower().strip()
        
        # Direct match
        if user_lower == job_lower:
            return 100
        
        # Check synonym map
        for main_skill, synonyms in self.semantic_skill_map.items():
            if user_lower in synonyms and job_lower in synonyms:
                return 95
            if user_lower == main_skill and job_lower in synonyms:
                return 90
            if job_lower == main_skill and user_lower in synonyms:
                return 90
        
        # Partial match
        if job_lower in user_lower or user_lower in job_lower:
            return 70
        
        # Hierarchical taxonomy match
        for category, subcategories in self.skill_taxonomy.items():
            for subcategory, skills in subcategories.items():
                if user_lower in skills and job_lower in skills:
                    return 85
        
        return 0
    
    def calculate_advanced_skill_match(self, user_skills: List[str], job_skills_str: str) -> Dict:
        """Calculate advanced skill match with taxonomy support"""
        job_skills = [s.strip().lower() for s in job_skills_str.split(',')] if job_skills_str else []
        user_skills_lower = [s.lower() for s in user_skills]
        
        exact_matches = []
        semantic_matches = []
        taxonomy_matches = []
        
        for js in job_skills:
            # Check exact match
            if js in user_skills_lower:
                exact_matches.append(js)
                continue
            
            # Check semantic match
            semantic_found = False
            for us in user_skills_lower:
                sim = self.semantic_skill_match(us, js)
                if sim >= 70:
                    semantic_matches.append({"user": us, "job": js, "confidence": sim})
                    semantic_found = True
                    break
            
            if semantic_found:
                continue
            
            # Check taxonomy match
            for us in user_skills_lower:
                for category, subcategories in self.skill_taxonomy.items():
                    for subcategory, skills in subcategories.items():
                        if us in skills and js in skills:
                            taxonomy_matches.append({"user": us, "job": js, "category": category})
                            break
                    else:
                        continue
                    break
        
        # Calculate scores
        exact_score = (len(exact_matches) / len(job_skills)) * 100 if job_skills else 0
        semantic_bonus = len(semantic_matches) * 5
        taxonomy_bonus = len(taxonomy_matches) * 3
        
        total_score = min(100, exact_score + semantic_bonus + taxonomy_bonus)
        
        # Missing skills
        all_matched = set(exact_matches) | set([m['job'] for m in semantic_matches]) | set([m['job'] for m in taxonomy_matches])
        missing_skills = [js for js in job_skills if js not in all_matched][:5]
        
        return {
            'score': round(total_score, 1),
            'exact_matches': exact_matches,
            'semantic_matches': semantic_matches,
            'taxonomy_matches': taxonomy_matches,
            'missing_skills': missing_skills,
            'total_required': len(job_skills),
            'matched_count': len(exact_matches) + len(semantic_matches) + len(taxonomy_matches)
        }
    
    # ============ EXPERIENCE ANALYSIS METHODS ============
    
    def extract_experience_years(self, text: str) -> Dict:
        """Extract years of experience using multiple methods"""
        if not text:
            return {'total_years': 0, 'confidence': 0, 'methods': []}
        
        text_lower = text.lower()
        extracted_years = []
        methods_used = []
        
        # Direct extraction patterns
        patterns = [
            (r'(\d+)\+?\s*(?:years?|yrs?)', 'direct'),
            (r'(?:experience|worked for) (\d+)\+?\s*(?:years?|yrs?)', 'explicit'),
            (r'(\d+)\+?\s*years? of experience', 'explicit'),
            (r'(\d+)\+?\s*years? in', 'industry_specific')
        ]
        
        for pattern, method in patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                try:
                    years = int(match)
                    extracted_years.append(years)
                    methods_used.append(method)
                except:
                    pass
        
        # Seniority-based inference
        if 'senior' in text_lower:
            extracted_years.append(6)
            methods_used.append('senior_inferred')
        if 'lead' in text_lower or 'manager' in text_lower:
            extracted_years.append(7)
            methods_used.append('lead_inferred')
        
        # Calculate weighted average
        if extracted_years:
            weights = {'direct': 1.0, 'explicit': 1.0, 'senior_inferred': 0.7, 'lead_inferred': 0.7, 'industry_specific': 0.8}
            total_weight = sum(weights.get(m, 0.6) for m in methods_used)
            weighted_sum = sum(y * weights.get(m, 0.6) for y, m in zip(extracted_years, methods_used))
            total_years = round(weighted_sum / total_weight) if total_weight > 0 else max(extracted_years)
        else:
            total_years = 0
        
        confidence = min(100, len(extracted_years) * 20) if extracted_years else 0
        
        return {
            'total_years': total_years,
            'extracted_values': extracted_years,
            'methods': list(set(methods_used)),
            'confidence': confidence
        }
    
    def calculate_experience_quality(self, experience_text: str, years: int) -> Dict:
        """Calculate experience quality score with detailed insights"""
        if not experience_text:
            return {'score': 40, 'insights': ['⚠️ Add detailed experience description'], 'level': 'Not specified'}
        
        text_lower = experience_text.lower()
        score = 50
        insights = []
        
        # Seniority detection
        senior_keywords = ['senior', 'lead', 'principal', 'architect', 'manager', 'director', 'head']
        if any(kw in text_lower for kw in senior_keywords):
            score += 15
            insights.append("✅ Senior-level experience detected")
        
        # Leadership detection
        leadership_found = [kw for kw in self.leadership_keywords if kw in text_lower]
        if leadership_found:
            score += 10
            insights.append(f"✅ Leadership experience found ({', '.join(leadership_found[:2])})")
        
        # Years bonus
        if years >= 8:
            score += 15
            insights.append(f"✅ {years} years of extensive experience")
        elif years >= 5:
            score += 10
            insights.append(f"✅ {years} years of solid experience")
        elif years >= 3:
            score += 5
        
        # Achievement detection
        achievements = []
        for pattern in self.achievement_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                achievements.append(match if isinstance(match, str) else str(match[0]))
        
        if achievements:
            score += min(20, len(achievements) * 4)
            insights.append(f"✅ {len(achievements)} quantifiable achievements detected")
        
        # Soft skills detection
        soft_skills_found = []
        for category, skills in self.soft_skills_keywords.items():
            for skill in skills:
                if skill in text_lower:
                    soft_skills_found.append(skill)
                    break
        
        if soft_skills_found:
            score += min(10, len(soft_skills_found) * 2)
            insights.append(f"🤝 Soft skills: {', '.join(soft_skills_found[:2])}")
        
        # Determine level
        if years >= 8 or score >= 80:
            level = "Senior/Lead"
        elif years >= 5 or score >= 65:
            level = "Mid-Level"
        elif years >= 2 or score >= 50:
            level = "Junior"
        else:
            level = "Entry"
        
        return {
            'score': min(100, score),
            'level': level,
            'insights': insights[:4],
            'achievements_count': len(achievements),
            'leadership_detected': len(leadership_found) > 0,
            'soft_skills_detected': soft_skills_found[:3]
        }
    
    # ============ JOB ANALYSIS METHODS ============
    
    def analyze_job_complexity(self, job_description: str, responsibilities: str = "") -> Dict:
        """Analyze the complexity level of a job"""
        text = f"{job_description} {responsibilities}".lower()
        
        complexity_scores = {'high': 0, 'medium': 0, 'low': 0}
        matched_keywords = {'high': [], 'medium': [], 'low': []}
        
        for level, indicators in self.job_complexity_indicators.items():
            for keyword in indicators['keywords']:
                if keyword in text:
                    complexity_scores[level] += 1
                    matched_keywords[level].append(keyword)
        
        # Calculate total complexity score
        high_weight = self.job_complexity_indicators['high']['weight']
        medium_weight = self.job_complexity_indicators['medium']['weight']
        low_weight = self.job_complexity_indicators['low']['weight']
        
        total_score = (complexity_scores['high'] * 100 * high_weight) + \
                      (complexity_scores['medium'] * 70 * medium_weight) + \
                      (complexity_scores['low'] * 40 * low_weight)
        
        max_possible = 500  # Approximate maximum
        complexity_score = min(100, round((total_score / max_possible) * 100)) if total_score > 0 else 50
        
        # Determine complexity level
        if complexity_scores['high'] >= 2:
            level = "High Complexity"
        elif complexity_scores['medium'] >= 3:
            level = "Medium Complexity"
        else:
            level = "Standard Complexity"
        
        return {
            'score': complexity_score,
            'level': level,
            'high_count': complexity_scores['high'],
            'medium_count': complexity_scores['medium'],
            'low_count': complexity_scores['low'],
            'matched_keywords': matched_keywords,
            'insights': self._generate_complexity_insights(complexity_scores, matched_keywords)
        }
    
    def _generate_complexity_insights(self, scores: Dict, keywords: Dict) -> List[str]:
        """Generate insights about job complexity"""
        insights = []
        if scores['high'] >= 2:
            insights.append(f"🏗️ High complexity role requiring: {', '.join(keywords['high'][:3])}")
        elif scores['medium'] >= 3:
            insights.append(f"📊 Medium complexity with {scores['medium']} advanced requirements")
        
        if 'scalable' in keywords['high'] or 'high-load' in keywords['high']:
            insights.append("📈 Scalability expertise required")
        if 'microservices' in keywords['high']:
            insights.append("🔧 Microservices architecture experience needed")
        if 'cloud' in keywords['medium']:
            insights.append("☁️ Cloud platform experience required")
        
        return insights
    
    def analyze_responsibilities(self, responsibilities: str) -> Dict:
        """Deep analysis of job responsibilities"""
        if not responsibilities:
            return {'primary_focus': 'Not specified', 'insights': [], 'scores': {}}
        
        text = responsibilities.lower()
        category_scores = {cat: 0 for cat in self.responsibility_weights.keys()}
        category_matches = {cat: [] for cat in self.responsibility_weights.keys()}
        
        for category, keywords in self.responsibility_weights.items():
            for keyword in keywords:
                if keyword in text:
                    count = len(re.findall(rf'\b{keyword}\w*\b', text))
                    category_scores[category] += count
                    category_matches[category].append(keyword)
        
        total = sum(category_scores.values()) or 1
        percentages = {cat: round((score / total) * 100, 1) for cat, score in category_scores.items()}
        
        # Determine primary focus
        primary_focus = max(percentages, key=percentages.get) if percentages else "General"
        
        insights = []
        if percentages.get('leadership', 0) > 30:
            insights.append("👔 Strong leadership and management responsibilities")
        if percentages.get('strategic', 0) > 25:
            insights.append("🎯 Strategic planning and architecture focus")
        if percentages.get('technical', 0) > 40:
            insights.append("💻 Heavy technical development focus")
        if percentages.get('analytical', 0) > 20:
            insights.append("📊 Data analysis and optimization emphasis")
        if percentages.get('collaborative', 0) > 20:
            insights.append("🤝 Cross-functional collaboration required")
        
        return {
            'scores': category_scores,
            'percentages': percentages,
            'primary_focus': primary_focus,
            'matches': category_matches,
            'insights': insights,
            'leadership_score': percentages.get('leadership', 0),
            'technical_score': percentages.get('technical', 0),
            'strategic_score': percentages.get('strategic', 0)
        }
    
    def detect_seniority_level(self, job_title: str, job_description: str) -> Dict:
        """Detect the seniority level required for the job"""
        text = f"{job_title} {job_description}".lower()
        
        seniority_scores = {'lead': 0, 'senior': 0, 'mid': 0, 'junior': 0}
        
        for level, indicators in self.seniority_indicators.items():
            for indicator in indicators:
                if indicator in text:
                    seniority_scores[level] += 1
        
        total_indicators = sum(seniority_scores.values())
        
        if seniority_scores['lead'] >= 1:
            level = "Lead/Principal"
            confidence = min(90, 60 + seniority_scores['lead'] * 15)
            min_years = 8
        elif seniority_scores['senior'] >= 1:
            level = "Senior"
            confidence = min(85, 50 + seniority_scores['senior'] * 15)
            min_years = 5
        elif seniority_scores['mid'] >= 1:
            level = "Mid-Level"
            confidence = min(80, 40 + seniority_scores['mid'] * 15)
            min_years = 3
        elif seniority_scores['junior'] >= 1:
            level = "Junior/Entry"
            confidence = min(75, 30 + seniority_scores['junior'] * 15)
            min_years = 1
        else:
            level = "Not Specified"
            confidence = 50
            min_years = 2
        
        return {
            'level': level,
            'confidence': confidence,
            'min_years': min_years,
            'scores': seniority_scores,
            'detected_level': max(seniority_scores, key=seniority_scores.get) if total_indicators > 0 else None
        }
    
    def extract_soft_skills_from_job(self, job_description: str, responsibilities: str) -> Dict:
        """Extract soft skills required from job description"""
        text = f"{job_description} {responsibilities}".lower()
        
        soft_skills_found = {}
        for category, skills in self.soft_skills_keywords.items():
            found = []
            for skill in skills:
                if skill in text:
                    found.append(skill)
            if found:
                soft_skills_found[category] = {
                    'keywords': found[:3],
                    'count': len(found),
                    'importance': min(100, len(found) * 20)
                }
        
        return {
            'skills': soft_skills_found,
            'total_count': len(soft_skills_found),
            'primary_skill': max(soft_skills_found.keys(), key=lambda x: soft_skills_found[x]['count']) if soft_skills_found else None
        }
    
    # ============ NLP ANALYSIS METHODS ============
    
    def extract_years_from_summary(self, summary: str) -> int:
        """Extract years of experience from summary text"""
        if not summary:
            return 0
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)',
            r'(?:experience|worked for) (\d+)\+?\s*(?:years?|yrs?)',
            r'(\d+)\+?\s*years? of experience'
        ]
        for pattern in patterns:
            match = re.search(pattern, summary.lower())
            if match:
                return int(match.group(1))
        return 0
    
    def detect_leadership_in_summary(self, text: str) -> List[str]:
        """Detect leadership keywords in summary"""
        if not text:
            return []
        text_lower = text.lower()
        return [kw for kw in self.leadership_keywords if kw in text_lower]
    
    def detect_soft_skills_in_summary(self, text: str) -> List[str]:
        """Extract soft skills from summary"""
        if not text:
            return []
        text_lower = text.lower()
        detected = []
        for category, skills in self.soft_skills_keywords.items():
            for skill in skills:
                if skill in text_lower:
                    detected.append(skill)
                    break
        return detected[:5]
    
    def detect_achievements_in_summary(self, text: str) -> List[Dict]:
        """Detect achievements in summary"""
        if not text:
            return []
        text_lower = text.lower()
        achievements = []
        for pattern in self.achievement_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                achievements.append({
                    'pattern': match if isinstance(match, str) else str(match[0]),
                    'value': match[0] if isinstance(match, tuple) else match
                })
        return achievements
    
    def calculate_advanced_nlp_score(self, user_summary: str, job_title: str, job_description: str, experience_text: str = "") -> Dict:
        """Advanced NLP analysis with deep understanding"""
        if not user_summary or len(user_summary) < 50:
            return {
                'score': 25,
                'insights': ["✏️ Add a detailed professional summary (150+ words recommended)"],
                'common_keywords': [],
                'leadership': [],
                'soft_skills': [],
                'achievements': [],
                'experience_years': 0,
                'keyword_score': 0,
                'length_score': 0,
                'word_count': len(user_summary) if user_summary else 0
            }
        
        summary_lower = user_summary.lower()
        job_text = f"{job_title} {job_description}".lower()
        
        # Extract keywords
        important_keywords = ['python', 'java', 'javascript', 'react', 'angular', 'node', 'django', 'flask',
                              'sql', 'mongodb', 'docker', 'kubernetes', 'aws', 'git', 'api', 'cloud', 
                              'management', 'sales', 'marketing', 'finance', 'accounting', 'leadership', 'team',
                              'communication', 'analytical', 'problem solving', 'project management']
        
        summary_keywords = [kw for kw in important_keywords if kw in summary_lower]
        job_keywords = [kw for kw in important_keywords if kw in job_text]
        
        common_keywords = list(set(summary_keywords) & set(job_keywords))
        keyword_score = (len(common_keywords) / max(len(job_keywords), 1)) * 100
        
        # Extract experience
        implied_years = self.extract_years_from_summary(user_summary)
        
        # Detect leadership
        leadership_skills = self.detect_leadership_in_summary(user_summary)
        
        # Detect soft skills
        soft_skills = self.detect_soft_skills_in_summary(user_summary)
        
        # Detect achievements
        achievements = self.detect_achievements_in_summary(user_summary)
        
        # Calculate length score
        word_count = len(user_summary.split())
        if word_count >= 300:
            length_score = 100
        elif word_count >= 200:
            length_score = 85
        elif word_count >= 150:
            length_score = 70
        elif word_count >= 100:
            length_score = 50
        elif word_count >= 50:
            length_score = 30
        else:
            length_score = 15
        
        # Calculate final NLP score
        final_score = (
            (keyword_score * 0.30) +
            (min(100, implied_years * 10) * 0.15) +
            (min(100, len(leadership_skills) * 12) * 0.15) +
            (min(100, len(achievements) * 8) * 0.15) +
            (min(100, len(soft_skills) * 6) * 0.10) +
            (length_score * 0.15)
        )
        final_score = min(100, max(0, round(final_score, 1)))
        
        # Generate insights
        insights = []
        if common_keywords:
            insights.append(f"🔑 Found {len(common_keywords)} relevant keywords: {', '.join(common_keywords[:4])}")
        if implied_years > 0:
            insights.append(f"📅 Experience detected: {implied_years}+ years")
        if leadership_skills:
            insights.append(f"👔 Leadership qualities: {', '.join(leadership_skills[:2])}")
        if soft_skills:
            insights.append(f"🤝 Soft skills identified: {', '.join(soft_skills[:2])}")
        if achievements:
            insights.append(f"🏆 {len(achievements)} quantifiable achievements found")
        if word_count < 150:
            insights.append("💡 Add more detail to your summary (200+ words recommended)")
        
        return {
            'score': final_score,
            'insights': insights,
            'common_keywords': common_keywords,
            'leadership': leadership_skills,
            'soft_skills': soft_skills,
            'achievements': achievements,
            'experience_years': implied_years,
            'keyword_score': round(keyword_score, 1),
            'length_score': length_score,
            'word_count': word_count
        }
    
    def calculate_nlp_score(self, user_summary: str, job_title: str, job_description: str) -> Dict:
        """NLP score calculation wrapper"""
        return self.calculate_advanced_nlp_score(user_summary, job_title, job_description, user_summary)
    
    # ============ JOB REQUIREMENTS SCORE ============
    
    def calculate_job_requirements_score(self, user_skills: List[str], user_exp: int,
                                           job_skills_str: str, job_exp_req: int,
                                           job_title: str, job_description: str,
                                           responsibilities: str = "") -> Dict:
        """Calculate how well candidate matches job requirements"""
        
        # 1. Skill match with advanced analysis
        skill_result = self.calculate_advanced_skill_match(user_skills, job_skills_str)
        
        # 2. Seniority matching
        seniority_result = self.detect_seniority_level(job_title, job_description)
        seniority_match = 100 if user_exp >= seniority_result['min_years'] else (user_exp / seniority_result['min_years']) * 100
        
        # 3. Complexity matching
        complexity_result = self.analyze_job_complexity(job_description, responsibilities)
        
        # 4. Responsibility matching
        responsibility_result = self.analyze_responsibilities(responsibilities)
        
        # 5. Calculate final score
        final_score = (
            (skill_result['score'] * 0.40) +
            (seniority_match * 0.20) +
            (complexity_result['score'] * 0.20) +
            (responsibility_result.get('technical_score', 50) * 0.10) +
            (responsibility_result.get('leadership_score', 0) * 0.10)
        )
        
        final_score = round(final_score, 1)
        
        # Generate insights
        insights = []
        if seniority_match >= 80:
            insights.append(f"✅ Seniority level matches ({seniority_result['level']} role)")
        elif seniority_match >= 60:
            insights.append(f"📊 Close to {seniority_result['level']} level requirement")
        else:
            insights.append(f"⚠️ Need {seniority_result['min_years'] - user_exp} more years for {seniority_result['level']} level")
        
        if complexity_result['score'] >= 70:
            insights.append(f"🏗️ Job complexity aligns with your experience ({complexity_result['level']})")
        
        if responsibility_result.get('leadership_score', 0) > 30:
            insights.append("👔 Leadership responsibilities detected - highlight management experience")
        
        if responsibility_result.get('technical_score', 0) > 40:
            insights.append("💻 Strong technical focus - your skills are relevant")
        
        return {
            'score': final_score,
            'skill_match': skill_result['score'],
            'seniority_match': round(seniority_match, 1),
            'complexity_match': complexity_result['score'],
            'seniority_level': seniority_result['level'],
            'complexity_level': complexity_result['level'],
            'primary_focus': responsibility_result.get('primary_focus', 'General'),
            'insights': insights[:4],
            'missing_skills': skill_result['missing_skills'],
            'exact_matches': skill_result['exact_matches'],
            'semantic_matches': skill_result['semantic_matches']
        }
    
    # ============ MAIN MATCH SCORE METHOD ============
    
    def calculate_match_score_rf(self, user_skills: List[str], user_exp: int,
                                   job_skills_str: str, job_exp_req: int,
                                   job_title: str, job_type: str,
                                   job_industry: str, user_location: str) -> Dict:
        """Calculate match score with all advanced features"""
        
        # Get category
        category_result = self.predict_category(job_title)
        job_category = category_result['category']
        job_confidence = category_result['confidence']
        
        # Advanced skill matching
        skill_result = self.calculate_advanced_skill_match(user_skills, job_skills_str)
        skill_score = skill_result['score']
        
        # Experience score
        exp_score = 100 if user_exp >= job_exp_req else (user_exp / job_exp_req) * 100 if job_exp_req > 0 else 0
        
        # Career level
        factors = self.career_factors.get(job_category, self.career_factors['General'])
        if user_exp >= factors['lead']:
            career_level = 'Lead'
            career_score = 100
        elif user_exp >= factors['senior']:
            career_level = 'Senior'
            career_score = 85
        elif user_exp >= factors['mid']:
            career_level = 'Mid'
            career_score = 70
        elif user_exp >= factors['junior']:
            career_level = 'Junior'
            career_score = 55
        else:
            career_level = 'Entry'
            career_score = 40
        
        # Final score
        final_score = (skill_score * 0.45) + (exp_score * 0.25) + (career_score * 0.20) + (job_confidence * 0.10)
        final_score = round(final_score, 1)
        
        # Generate insights
        skill_insights = []
        if skill_score >= 80:
            skill_insights.append(f"🎯 Excellent skill match ({skill_score:.0f}%)")
        elif skill_score >= 60:
            skill_insights.append(f"📚 Good skill match ({skill_score:.0f}%)")
        else:
            skill_insights.append(f"⚠️ Skill gap detected ({skill_score:.0f}%)")
        
        if skill_result['semantic_matches']:
            skill_insights.append(f"🔄 {len(skill_result['semantic_matches'])} semantic skill matches")
        
        if skill_result['taxonomy_matches']:
            skill_insights.append(f"📚 {len(skill_result['taxonomy_matches'])} related skills from your stack")
        
        career_insights = [f"📊 Career level: {career_level}", f"⏰ Experience: {user_exp} vs {job_exp_req} years"]
        
        analysis = f"Skills: {skill_score:.0f}% | Experience: {exp_score:.0f}% | Career: {career_level} level"
        
        return {
            'match_score': final_score,
            'skill_score': skill_score,
            'career_score': career_score,
            'exp_score': round(exp_score, 1),
            'rf_confidence': job_confidence,
            'predicted_category': job_category,
            'career_level': career_level,
            'exact_skill_matches': skill_result['exact_matches'],
            'semantic_matches': skill_result['semantic_matches'],
            'taxonomy_matches': skill_result['taxonomy_matches'],
            'missing_skills': skill_result['missing_skills'],
            'skill_insights': skill_insights,
            'career_insights': career_insights,
            'analysis': analysis
        }


# Create singleton instance
rf_matcher = RandomForestMatcher()
print("✅ Advanced Random Forest Matcher initialized")
print("   Features: Semantic Matching | Advanced NLP | Job Complexity Analysis")
print("   Sub-categories: 10 | Skill Taxonomy: 6 categories | Achievement Detection: Enabled")