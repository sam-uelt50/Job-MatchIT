# backend/rf_predictor.py
import pickle
import pandas as pd
import numpy as np
import re
import os

class EthiopianJobPredictor:
    def __init__(self):
        model_path = "ml_models/"
        self.model = pickle.load(open(f"{model_path}ethiopian_job_rf_model.pkl", "rb"))
        self.scaler = pickle.load(open(f"{model_path}ethiopian_rf_scaler.pkl", "rb"))
        self.encoder = pickle.load(open(f"{model_path}ethiopian_rf_encoder.pkl", "rb"))
        print("✅ Ethiopian Job Predictor loaded")
    
    def extract_features(self, job_title, job_type='', sector='', location='', experience=''):
        """Extract features from job data"""
        title_lower = job_title.lower()
        
        def contains_english(text):
            return bool(re.search(r'[a-zA-Z]', str(text)))
        
        feature = {
            'title_length': min(len(job_title), 100),
            'title_word_count': len(job_title.split()),
            'has_english': 1 if contains_english(title_lower) else 0,
            'has_senior': 1 if 'senior' in title_lower or 'sr' in title_lower else 0,
            'has_junior': 1 if 'junior' in title_lower or 'jr' in title_lower or 'entry' in title_lower else 0,
            'has_lead': 1 if any(x in title_lower for x in ['lead', 'manager', 'head', 'supervisor', 'director']) else 0,
            'has_assistant': 1 if 'assistant' in title_lower or 'aide' in title_lower else 0,
            'has_developer': 1 if any(x in title_lower for x in ['developer', 'engineer', 'programmer', 'coder']) else 0,
            'has_python': 1 if 'python' in title_lower else 0,
            'has_javascript': 1 if any(x in title_lower for x in ['javascript', 'js', 'react', 'angular', 'vue', 'node']) else 0,
            'has_java': 1 if 'java' in title_lower else 0,
            'has_sql': 1 if any(x in title_lower for x in ['sql', 'database', 'mysql', 'postgres']) else 0,
            'has_web': 1 if any(x in title_lower for x in ['web', 'frontend', 'backend', 'full stack']) else 0,
            'has_sales': 1 if any(x in title_lower for x in ['sales', 'marketing', 'business', 'bd']) else 0,
            'has_accounting': 1 if any(x in title_lower for x in ['accountant', 'accounting', 'finance', 'cashier', 'audit', 'tax']) else 0,
            'has_hr': 1 if any(x in title_lower for x in ['hr', 'human resources', 'recruitment', 'talent']) else 0,
            'has_admin': 1 if any(x in title_lower for x in ['admin', 'secretary', 'reception', 'office', 'assistant']) else 0,
            'has_manager': 1 if 'manager' in title_lower or 'management' in title_lower else 0,
            'has_medical': 1 if any(x in title_lower for x in ['nurse', 'doctor', 'medical', 'health', 'clinical', 'patient', 'hospital']) else 0,
            'has_teaching': 1 if any(x in title_lower for x in ['teacher', 'instructor', 'professor', 'trainer', 'tutor']) else 0,
            'has_amharic': 1 if not contains_english(title_lower) and len(title_lower) > 3 else 0,
            'is_remote': 1 if 'remote' in job_type.lower() else 0,
            'is_fulltime': 1 if 'full' in job_type.lower() or 'permanent' in job_type.lower() else 0,
            'is_parttime': 1 if 'part' in job_type.lower() or 'hourly' in job_type.lower() else 0,
            'is_contract': 1 if 'contract' in job_type.lower() else 0,
            'is_tech_sector': 1 if 'technology' in str(sector).lower() or 'it' in str(sector).lower() else 0,
            'is_finance_sector': 1 if 'finance' in str(sector).lower() or 'bank' in str(sector).lower() else 0,
            'is_health_sector': 1 if 'health' in str(sector).lower() or 'medical' in str(sector).lower() else 0,
            'is_addis': 1 if 'addis' in location.lower() else 0,
            'is_remote_location': 1 if 'remote' in location.lower() else 0,
            'exp_senior': 1 if 'senior' in experience.lower() or '5+' in experience else 0,
            'exp_mid': 1 if 'mid' in experience.lower() or '3-5' in experience else 0,
            'exp_entry': 1 if 'entry' in experience.lower() or 'junior' in experience.lower() else 0,
            'desc_length': 0,
            'desc_has_description': 0,
        }
        return pd.DataFrame([feature])
    
    def predict(self, job_title, job_type='', sector='', location='', experience=''):
        """Predict job category"""
        X = self.extract_features(job_title, job_type, sector, location, experience)
        X_scaled = self.scaler.transform(X)
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]
        
        category = self.encoder.inverse_transform([prediction])[0]
        confidence = max(probabilities) * 100
        
        # Get all probabilities
        all_probs = {}
        for i, prob in enumerate(probabilities):
            cat = self.encoder.inverse_transform([i])[0]
            all_probs[cat] = round(prob * 100, 1)
        
        return {
            'category': category,
            'confidence': round(confidence, 1),
            'all_probabilities': all_probs
        }

# Test the model
if __name__ == "__main__":
    predictor = EthiopianJobPredictor()
    
    test_jobs = [
        "Senior Python Developer",
        "Accountant",
        "Sales Manager",
        "Nurse",
        "Teacher",
        "Software Engineer",
        "Cashier",
        "HR Officer"
    ]
    
    print("\n" + "="*60)
    print("🧪 TESTING RANDOM FOREST PREDICTIONS")
    print("="*60)
    
    for job in test_jobs:
        result = predictor.predict(job)
        print(f"\n📌 '{job}'")
        print(f"   → Predicted: {result['category']} (Confidence: {result['confidence']}%)")
        print(f"   → All probabilities: {result['all_probabilities']}")