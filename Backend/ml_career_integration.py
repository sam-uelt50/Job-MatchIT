
import sqlite3
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'job_recruitment.db')

class CareerPathML:
    def __init__(self):
        self.vectorizer = None
        self.job_vectors = None
        self.job_titles = []
        self.career_transitions = {}
        self.model_path = os.path.join(os.path.dirname(__file__), "ml_models/")
        
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)
        
        self.load_models()
    
    def load_models(self):
        try:
            with open(f"{self.model_path}career_vectorizer.pkl", "rb") as f:
                self.vectorizer = pickle.load(f)
            with open(f"{self.model_path}job_vectors.pkl", "rb") as f:
                self.job_vectors = pickle.load(f)
            with open(f"{self.model_path}job_titles.pkl", "rb") as f:
                self.job_titles = pickle.load(f)
            with open(f"{self.model_path}career_transitions.pkl", "rb") as f:
                self.career_transitions = pickle.load(f)
            print("✅ Loaded career path ML models")
            return True
        except Exception as e:
            print(f"⚠️ No existing models found: {e}")
            return False
    
    def save_models(self):
        with open(f"{self.model_path}career_vectorizer.pkl", "wb") as f:
            pickle.dump(self.vectorizer, f)
        with open(f"{self.model_path}job_vectors.pkl", "wb") as f:
            pickle.dump(self.job_vectors, f)
        with open(f"{self.model_path}job_titles.pkl", "wb") as f:
            pickle.dump(self.job_titles, f)
        with open(f"{self.model_path}career_transitions.pkl", "wb") as f:
            pickle.dump(self.career_transitions, f)
        print("✅ Saved career path ML models")
    
    def load_career_paths_from_csv(self, csv_path):
        if not os.path.exists(csv_path):
            print(f"❌ CSV file not found: {csv_path}")
            return False
        
        df = pd.read_csv(csv_path)
        print(f"📊 Loaded {len(df)} career paths from CSV")
        print(f"📋 Columns found: {list(df.columns)}")
        
        # Use Past_Jobs_Internships and Suggested_Career_Path columns
        job_cols = ['Past_Jobs_Internships', 'Suggested_Career_Path']
        
        # Extract job titles
        all_titles = set()
        for col in job_cols:
            if col in df.columns:
                titles = df[col].dropna().astype(str).tolist()
                for title in titles:
                    if title and title != 'nan' and len(title) > 1:
                        all_titles.add(title.strip())
        
        self.job_titles = list(all_titles)
        print(f"✅ Found {len(self.job_titles)} unique job titles")
        
        # Build career transitions
        if 'Past_Jobs_Internships' in df.columns and 'Suggested_Career_Path' in df.columns:
            for idx, row in df.iterrows():
                from_job = row['Past_Jobs_Internships']
                to_job = row['Suggested_Career_Path']
                if pd.notna(from_job) and pd.notna(to_job):
                    from_job = str(from_job).strip()
                    to_job = str(to_job).strip()
                    if from_job and to_job and from_job != 'nan' and to_job != 'nan':
                        key = (from_job, to_job)
                        self.career_transitions[key] = self.career_transitions.get(key, 0) + 1
        
        print(f"✅ Found {len(self.career_transitions)} unique career transitions")
        
        self._save_to_database()
        return True
    
    def _save_to_database(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS career_paths (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_job TEXT,
                to_job TEXT,
                transition_count INTEGER,
                created_at TEXT
            )
        ''')
        
        cursor.execute("DELETE FROM career_paths")
        
        for (from_job, to_job), count in self.career_transitions.items():
            cursor.execute('''
                INSERT INTO career_paths (from_job, to_job, transition_count, created_at)
                VALUES (?, ?, ?, ?)
            ''', (from_job, to_job, count, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        print(f"✅ Saved {len(self.career_transitions)} transitions to database")
    
    def train_job_similarity(self):
        if not self.job_titles:
            print("❌ No job titles found. Load CSV first.")
            return False
        
        # Filter out empty or invalid titles
        valid_titles = [t for t in self.job_titles if t and len(t) > 1]
        
        if not valid_titles:
            print("❌ No valid job titles found.")
            return False
        
        self.vectorizer = TfidfVectorizer(
            analyzer='char', 
            ngram_range=(2, 5),
            max_features=500,
            lowercase=True
        )
        self.job_vectors = self.vectorizer.fit_transform(valid_titles)
        self.job_titles = valid_titles
        
        self.save_models()
        print(f"✅ Trained job similarity model on {len(self.job_titles)} titles")
        return True
    
    def find_similar_jobs(self, job_title, top_n=10):
        # Check if models exist properly
        if self.vectorizer is None:
            print("Vectorizer not loaded, attempting to load...")
            if not self.load_models():
                return []
        
        # Check if job_vectors has data
        if self.job_vectors is None:
            print("Job vectors not available")
            return []
        
        try:
            # Check if job_vectors has any rows
            if self.job_vectors.shape[0] == 0:
                print("No job vectors available")
                return []
        except:
            return []
        
        if not job_title or job_title == "":
            return []
        
        try:
            input_vec = self.vectorizer.transform([job_title.lower()])
            similarities = cosine_similarity(input_vec, self.job_vectors)[0]
            top_indices = similarities.argsort()[-top_n:][::-1]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.1 and idx < len(self.job_titles):
                    results.append({
                        'title': self.job_titles[idx],
                        'similarity': round(float(similarities[idx]) * 100, 1)
                    })
            return results
        except Exception as e:
            print(f"Error finding similar jobs: {e}")
            return []
    
    def predict_career_path(self, current_job, top_n=5):
        if not self.career_transitions:
            return []
        
        similar_jobs = self.find_similar_jobs(current_job, top_n=5)
        
        next_steps = {}
        for job in similar_jobs:
            for (from_job, to_job), count in self.career_transitions.items():
                if from_job.lower() == job['title'].lower():
                    next_steps[to_job] = next_steps.get(to_job, 0) + count
        
        total = sum(next_steps.values())
        sorted_steps = sorted(next_steps.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        return [{
            'title': title, 
            'confidence': round((count / total) * 100, 1) if total > 0 else 0,
            'transition_count': count
        } for title, count in sorted_steps]
    
    def get_career_insights(self, user_job_title):
        similar_jobs = self.find_similar_jobs(user_job_title, top_n=5)
        next_steps = self.predict_career_path(user_job_title, top_n=5)
        
        return {
            'current_role': user_job_title,
            'similar_roles': similar_jobs,
            'suggested_next_roles': next_steps,
            'has_career_data': len(self.career_transitions) > 0
        }

career_ml = CareerPathML()