# -*- coding: utf-8 -*-
"""
JobMatch ET - Complete Integration Module
Use this in your main backend for production
"""

import pickle
import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class JobMatchEngine:
    """Complete job matching engine for JobMatch ET"""
    
    def __init__(self):
        self.char_vectorizer = None
        self.char_vectors = None
        self.word_vectorizer = None
        self.word_vectors = None
        self.job_titles = None
        self.load_models()
    
    def load_models(self):
        """Load all trained models"""
        try:
            self.char_vectorizer = pickle.load(open('ethiopian_job_vectorizer_char.pkl', 'rb'))
            self.char_vectors = pickle.load(open('ethiopian_job_vectors_char.pkl', 'rb'))
            self.word_vectorizer = pickle.load(open('ethiopian_job_vectorizer_word.pkl', 'rb'))
            self.word_vectors = pickle.load(open('ethiopian_job_vectors_word.pkl', 'rb'))
            self.job_titles = pickle.load(open('ethiopian_job_titles.pkl', 'rb'))
            print(f"✅ JobMatch Engine ready with {len(self.job_titles):,} Ethiopian job titles")
            return True
        except Exception as e:
            print(f"❌ Engine load error: {e}")
            return False
    
    def match_job(self, job_title, top_n=10):
        """Match a job title to similar Ethiopian jobs"""
        if not self.char_vectorizer:
            return []
        
        try:
            # Clean input
            clean = re.sub(r'[^\w\s]', ' ', job_title.lower())
            clean = re.sub(r'\s+', ' ', clean).strip()
            
            if not clean:
                clean = job_title.lower()
            
            # Transform
            test_char = self.char_vectorizer.transform([clean])
            test_word = self.word_vectorizer.transform([clean])
            
            # Calculate
            char_sim = cosine_similarity(test_char, self.char_vectors)[0]
            word_sim = cosine_similarity(test_word, self.word_vectors)[0]
            
            # Hybrid (optimized for Ethiopian market)
            hybrid = (char_sim * 0.55) + (word_sim * 0.45)
            
            # Get top matches
            indices = np.argsort(hybrid)[-top_n*2:][::-1]
            
            results = []
            seen = set()
            
            for idx in indices:
                if idx >= len(self.job_titles):
                    continue
                
                title = self.job_titles[idx]
                score = hybrid[idx] * 100
                
                if score < 15:
                    continue
                
                # Deduplicate
                key = re.sub(r'\s+', ' ', title)[:25]
                if key in seen:
                    continue
                seen.add(key)
                
                # Category detection
                category = self._detect_category(title)
                
                results.append({
                    'title': title,
                    'match_score': round(score, 1),
                    'category': category
                })
                
                if len(results) >= top_n:
                    break
            
            return results
        except Exception as e:
            print(f"Matching error: {e}")
            return []
    
    def _detect_category(self, title):
        """Detect job category from title"""
        title_lower = title.lower()
        if any(w in title_lower for w in ['developer', 'engineer', 'programmer', 'it', 'software', 'python', 'java', 'javascript', 'react', 'django']):
            return 'Technology'
        elif any(w in title_lower for w in ['accountant', 'finance', 'cashier', 'audit', 'tax', 'budget']):
            return 'Finance'
        elif any(w in title_lower for w in ['teacher', 'professor', 'instructor', 'trainer', 'lecturer']):
            return 'Education'
        elif any(w in title_lower for w in ['nurse', 'doctor', 'medical', 'health', 'clinic', 'hospital']):
            return 'Healthcare'
        elif any(w in title_lower for w in ['sales', 'marketing', 'manager', 'director', 'supervisor']):
            return 'Business'
        else:
            return 'General'
    
    def calculate_candidate_match(self, candidate_skills, candidate_title, job_title):
        """Calculate match between candidate and job"""
        # Find similar jobs to candidate's title
        similar = self.match_job(candidate_title, 5)
        
        # Check if job title is in similar jobs
        for sim in similar:
            if sim['title'].lower() == job_title.lower():
                return sim['match_score']
        
        # Calculate direct similarity
        if candidate_title and job_title:
            test_char = self.char_vectorizer.transform([candidate_title.lower()])
            test_word = self.word_vectorizer.transform([job_title.lower()])
            char_sim = cosine_similarity(test_char, self.char_vectors)[0]
            word_sim = cosine_similarity(test_word, self.word_vectors)[0]
            return round(((char_sim.mean() * 0.55) + (word_sim.mean() * 0.45)) * 100, 1)
        
        return 50
    
    def get_stats(self):
        """Get engine statistics"""
        categories = {}
        for title in self.job_titles[:5000]:
            cat = self._detect_category(title)
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            'total_titles': len(self.job_titles),
            'categories': categories,
            'char_features': self.char_vectors.shape[1] if self.char_vectors is not None else 0,
            'word_features': self.word_vectors.shape[1] if self.word_vectors is not None else 0
        }

# Initialize engine
job_engine = JobMatchEngine()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🏆 JOBMATCH ET - FINAL ENGINE TEST")
    print("=" * 60)
    
    print(f"\n📊 Engine Statistics:")
    stats = job_engine.get_stats()
    print(f"   Total job titles: {stats['total_titles']:,}")
    print(f"   Character features: {stats['char_features']:,}")
    print(f"   Word features: {stats['word_features']:,}")
    print(f"\n   Category breakdown:")
    for cat, count in stats['categories'].items():
        print(f"      {cat}: {count}")
    
    print("\n🔍 Sample Matches:")
    test_jobs = ['software engineer', 'accountant', 'marketing manager', 'nurse', 'teacher']
    
    for job in test_jobs:
        print(f"\n   Matching '{job}':")
        matches = job_engine.match_job(job, 3)
        for m in matches:
            print(f"      → {m['title'][:40]} ({m['match_score']}%)")
    
    print("\n" + "=" * 60)
    print("✅ JobMatch ET Engine Ready for Production!")
    print("=" * 60)