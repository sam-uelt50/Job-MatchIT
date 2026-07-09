import re
import nltk
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except:
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('wordnet')

class NLPProfileAnalyzer:
    """Advanced NLP analysis for professional summaries and CV text"""
    
    def __init__(self):
        self.skill_keywords = {
            'technical': ['python', 'java', 'javascript', 'react', 'angular', 'node', 'django', 'flask', 
                         'sql', 'mongodb', 'docker', 'kubernetes', 'aws', 'azure', 'git', 'api', 'rest',
                         'machine learning', 'ai', 'tensorflow', 'pytorch', 'data science', 'analytics'],
            'soft_skills': ['leadership', 'communication', 'teamwork', 'problem solving', 'critical thinking',
                          'project management', 'agile', 'scrum', 'mentoring', 'collaboration'],
            'achievements': ['developed', 'built', 'created', 'designed', 'implemented', 'led', 'managed',
                           'improved', 'increased', 'reduced', 'achieved', 'won', 'awarded', 'published']
        }
    
    def extract_entities(self, text):
        """Extract named entities and key phrases from text"""
        blob = TextBlob(text)
        
        # Extract noun phrases (potential skills/technologies)
        noun_phrases = list(set(blob.noun_phrases))
        
        # Extract parts of speech
        pos_tags = blob.tags
        
        # Find capitalized words (potential proper nouns - technologies, companies)
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        return {
            'noun_phrases': noun_phrases[:20],
            'technologies': list(set(capitalized))[:15],
            'key_terms': self.extract_key_terms(text)
        }
    
    def extract_key_terms(self, text):
        """Extract important terms using TF-IDF on the text itself"""
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        word_freq = {}
        for w in words:
            if w not in ['and', 'the', 'for', 'with', 'have', 'are', 'was', 'were']:
                word_freq[w] = word_freq.get(w, 0) + 1
        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:15]]
    
    def extract_skills_from_summary(self, text):
        """Extract skills from professional summary using NLP"""
        text_lower = text.lower()
        found_skills = []
        
        for category, skills in self.skill_keywords.items():
            for skill in skills:
                if skill in text_lower:
                    found_skills.append(skill.title())
        
        # Also extract from noun phrases
        blob = TextBlob(text)
        for np in blob.noun_phrases:
            if len(np) > 2 and len(np) < 25:
                found_skills.append(np.title())
        
        return list(dict.fromkeys(found_skills))[:20]
    
    def analyze_sentiment(self, text):
        """Analyze sentiment and tone of the professional summary"""
        blob = TextBlob(text)
        sentiment = blob.sentiment
        
        # Determine tone
        if sentiment.polarity > 0.2:
            tone = "positive"
        elif sentiment.polarity < -0.2:
            tone = "negative"
        else:
            tone = "neutral"
        
        # Subjectivity (0=objective, 1=subjective)
        if sentiment.subjectivity > 0.6:
            style = "passionate/opinionated"
        else:
            style = "professional/factual"
        
        return {
            "polarity": round(sentiment.polarity, 2),
            "subjectivity": round(sentiment.subjectivity, 2),
            "tone": tone,
            "style": style
        }
    
    def calculate_experience_level(self, text):
        """Infer experience level from summary language"""
        text_lower = text.lower()
        experience_indicators = {
            'senior': ['senior', 'lead', 'principal', 'architect', 'manager', 'director'],
            'mid': ['experienced', 'mid-level', 'professional', 'developer', 'engineer'],
            'junior': ['junior', 'entry', 'associate', 'recent graduate', 'intern']
        }
        
        for level, indicators in experience_indicators.items():
            for ind in indicators:
                if ind in text_lower:
                    return level
        return 'mid'
    
    def calculate_summary_score(self, candidate_summary, job_title, job_description):
        """Calculate match score based on semantic understanding of the summary"""
        
        if not candidate_summary or not job_title:
            return 50
        
        # Extract entities and skills from summary
        summary_skills = self.extract_skills_from_summary(candidate_summary)
        summary_entities = self.extract_entities(candidate_summary)
        
        # Create TF-IDF vectors for semantic similarity
        documents = [
            candidate_summary,
            f"{job_title} {job_description}"
        ]
        
        vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
        tfidf_matrix = vectorizer.fit_transform(documents)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        # Semantic similarity score (0-100)
        semantic_score = similarity * 100
        
        # Job title presence in summary
        title_words = job_title.lower().split()
        title_matches = sum(1 for word in title_words if word in candidate_summary.lower())
        title_score = (title_matches / len(title_words)) * 100 if title_words else 50
        
        # Skill relevance
        job_skills = self.extract_skills_from_summary(job_description)
        if job_skills and summary_skills:
            matched_skills = [s for s in job_skills if s.lower() in [ss.lower() for ss in summary_skills]]
            skill_score = (len(matched_skills) / len(job_skills)) * 100 if job_skills else 50
        else:
            skill_score = 50
        
        # Experience level alignment
        exp_level = self.calculate_experience_level(candidate_summary)
        if 'senior' in job_title.lower() and exp_level == 'senior':
            exp_score = 100
        elif 'senior' in job_title.lower() and exp_level == 'mid':
            exp_score = 60
        else:
            exp_score = 80
        
        # Weighted final score: 40% semantic + 30% title + 20% skills + 10% experience
        final_score = (semantic_score * 0.4) + (title_score * 0.3) + (skill_score * 0.2) + (exp_score * 0.1)
        final_score = min(100, max(0, round(final_score)))
        
        return {
            "score": final_score,
            "semantic_similarity": round(semantic_score, 1),
            "title_relevance": round(title_score, 1),
            "skill_relevance": round(skill_score, 1),
            "experience_alignment": round(exp_score, 1),
            "sentiment": self.analyze_sentiment(candidate_summary),
            "extracted_skills": summary_skills[:10],
            "key_phrases": summary_entities['key_terms'][:10]
        }

# Create a global instance
nlp_analyzer = NLPProfileAnalyzer()

def analyze_summary_deep(summary_text, job_title, job_description=""):
    """Main function to analyze summary with deep NLP"""
    return nlp_analyzer.calculate_summary_score(summary_text, job_title, job_description)