# -*- coding: utf-8 -*-
import pickle
import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class JobMatcherAPI:
    """Production-ready job matcher for JobMatch ET"""
    
    def __init__(self):
        self.char_vectorizer = None
        self.char_vectors = None
        self.word_vectorizer = None
        self.word_vectors = None
        self.job_titles = None
        self.load_models()
    
    def load_models(self):
        try:
            self.char_vectorizer = pickle.load(open('ethiopian_job_vectorizer_char.pkl', 'rb'))
            self.char_vectors = pickle.load(open('ethiopian_job_vectors_char.pkl', 'rb'))
            self.word_vectorizer = pickle.load(open('ethiopian_job_vectorizer_word.pkl', 'rb'))
            self.word_vectors = pickle.load(open('ethiopian_job_vectors_word.pkl', 'rb'))
            self.job_titles = pickle.load(open('ethiopian_job_titles.pkl', 'rb'))
            print(f"✅ JobMatcherAPI loaded with {len(self.job_titles):,} Ethiopian job titles")
            return True
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            return False
    
    def find_similar(self, job_title, top_n=10, min_score=20):
        """Find similar jobs with detailed scoring"""
        try:
            # Clean input
            clean_input = re.sub(r'[^\w\s]', ' ', job_title.lower())
            clean_input = re.sub(r'\s+', ' ', clean_input).strip()
            
            if not clean_input:
                clean_input = job_title.lower()
            
            # Transform
            test_char = self.char_vectorizer.transform([clean_input])
            test_word = self.word_vectorizer.transform([clean_input])
            
            # Calculate similarities
            char_sim = cosine_similarity(test_char, self.char_vectors)[0]
            word_sim = cosine_similarity(test_word, self.word_vectors)[0]
            
            # Hybrid score (optimized for Ethiopian market)
            hybrid = (char_sim * 0.55) + (word_sim * 0.45)
            
            # Get top matches
            top_indices = np.argsort(hybrid)[-top_n*2:][::-1]
            
            results = []
            seen = set()
            
            for idx in top_indices:
                if idx >= len(self.job_titles):
                    continue
                
                title = self.job_titles[idx]
                score = hybrid[idx] * 100
                
                if score < min_score:
                    continue
                
                # Avoid duplicates
                key = re.sub(r'\s+', ' ', title)[:30]
                if key in seen:
                    continue
                seen.add(key)
                
                # Calculate relevance bonus
                original_words = set(job_title.lower().split())
                title_words = set(title.split())
                if original_words:
                    relevance = len(original_words & title_words) / len(original_words) * 100
                else:
                    relevance = 50
                
                results.append({
                    'job_title': title,
                    'match_score': round(score, 1),
                    'relevance': round(relevance, 1),
                    'skill_match': round(word_sim[idx] * 100, 1),
                    'text_match': round(char_sim[idx] * 100, 1)
                })
                
                if len(results) >= top_n:
                    break
            
            return results
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    def get_job_categories(self):
        """Get job categories from titles"""
        categories = {}
        for title in self.job_titles[:1000]:
            # Simple categorization by keyword
            if any(w in title for w in ['developer', 'programmer', 'engineer', 'coder']):
                cat = 'Technology'
            elif any(w in title for w in ['accountant', 'finance', 'cashier', 'audit']):
                cat = 'Finance'
            elif any(w in title for w in ['teacher', 'professor', 'instructor', 'trainer']):
                cat = 'Education'
            elif any(w in title for w in ['nurse', 'doctor', 'medical', 'health']):
                cat = 'Healthcare'
            elif any(w in title for w in ['sales', 'marketing', 'manager', 'director']):
                cat = 'Business'
            else:
                cat = 'Other'
            
            categories[cat] = categories.get(cat, 0) + 1
        
        return categories

# Create global instance
job_matcher = JobMatcherAPI()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🏆 JOB MATCHER API TEST")
    print("=" * 60)
    
    test_jobs = [
        'software engineer',
        'accountant',
        'marketing manager',
        'project manager',
        'data scientist',
        'graphic designer'
    ]
    
    for job in test_jobs:
        print(f"\n📌 Matching for: '{job}'")
        matches = job_matcher.find_similar(job, 5)
        for i, m in enumerate(matches, 1):
            print(f"   {i}. {m['job_title']} (Score: {m['match_score']}%)")
    
    print("\n📊 Job Categories Distribution:")
    for cat, count in job_matcher.get_job_categories().items():
        print(f"   {cat}: {count}")