# backend/enhanced_rf_predictor.py
import pickle
import pandas as pd
import numpy as np
import re
import os

class EnhancedJobPredictor:
    def __init__(self):
        model_path = "ml_models/"
        self.rf_model = pickle.load(open(f"{model_path}enhanced_rf_model.pkl", "rb"))
        self.scaler = pickle.load(open(f"{model_path}enhanced_scaler.pkl", "rb"))
        self.encoder = pickle.load(open(f"{model_path}enhanced_encoder.pkl", "rb"))
        print("✅ Enhanced Job Predictor loaded (60+ features, Ensemble model)")
    
    def extract_features(self, job_title, job_type='', sector='', location='', experience='', description=''):
        """Extract enhanced features from job data"""
        title_lower = job_title.lower()
        
        def contains_english(text):
            return bool(re.search(r'[a-zA-Z]', str(text)))
        
        feature = {
            # Basic title features
            'title_length': min(len(job_title), 100),
            'title_word_count': len(job_title.split()),
            'has_english': 1 if contains_english(title_lower) else 0,
            'has_amharic': 1 if not contains_english(title_lower) and len(title_lower) > 3 else 0,
            'title_complexity': len(set(title_lower.split())),
            
            # Seniority features
            'has_senior': 1 if 'senior' in title_lower or 'sr' in title_lower else 0,
            'has_junior': 1 if 'junior' in title_lower or 'jr' in title_lower or 'entry' in title_lower else 0,
            'has_lead': 1 if any(x in title_lower for x in ['lead', 'manager', 'head', 'supervisor', 'director']) else 0,
            'has_assistant': 1 if 'assistant' in title_lower or 'aide' in title_lower else 0,
            'has_intern': 1 if 'intern' in title_lower or 'trainee' in title_lower else 0,
            'has_principal': 1 if 'principal' in title_lower or 'staff' in title_lower else 0,
            'seniority_score': (1 if 'senior' in title_lower else 0) * 3 + (1 if any(x in title_lower for x in ['lead', 'manager']) else 0) * 2,
            
            # Technology keywords
            'has_developer': 1 if any(x in title_lower for x in ['developer', 'engineer', 'programmer', 'coder', 'software']) else 0,
            'has_python': 1 if 'python' in title_lower else 0,
            'has_javascript': 1 if any(x in title_lower for x in ['javascript', 'js', 'react', 'angular', 'vue', 'node']) else 0,
            'has_java': 1 if 'java' in title_lower else 0,
            'has_sql': 1 if any(x in title_lower for x in ['sql', 'database', 'mysql', 'postgres', 'oracle']) else 0,
            'has_frontend': 1 if any(x in title_lower for x in ['frontend', 'front-end', 'ui', 'ux', 'css', 'html']) else 0,
            'has_backend': 1 if any(x in title_lower for x in ['backend', 'back-end', 'api', 'server', 'microservice']) else 0,
            'has_fullstack': 1 if any(x in title_lower for x in ['full stack', 'fullstack', 'full-stack']) else 0,
            'has_devops': 1 if any(x in title_lower for x in ['devops', 'ci/cd', 'jenkins', 'gitlab']) else 0,
            'has_cloud': 1 if any(x in title_lower for x in ['aws', 'azure', 'gcp', 'cloud', 'lambda', 'ec2']) else 0,
            'has_docker': 1 if any(x in title_lower for x in ['docker', 'kubernetes', 'k8s', 'container']) else 0,
            'has_mobile': 1 if any(x in title_lower for x in ['android', 'ios', 'mobile', 'flutter', 'react native', 'swift', 'kotlin']) else 0,
            'has_data_science': 1 if any(x in title_lower for x in ['data science', 'machine learning', 'ai', 'tensorflow', 'pytorch', 'nlp']) else 0,
            'has_cyber': 1 if any(x in title_lower for x in ['security', 'cyber', 'penetration', 'ethical hacking']) else 0,
            'has_web': 1 if any(x in title_lower for x in ['web', 'website', 'www', 'internet']) else 0,
            'has_system': 1 if 'system' in title_lower or 'infrastructure' in title_lower else 0,
            'has_network': 1 if 'network' in title_lower or 'cisco' in title_lower else 0,
            'has_testing': 1 if any(x in title_lower for x in ['test', 'qa', 'quality', 'automation']) else 0,
            'tech_skill_count': sum([1 for x in ['has_python', 'has_javascript', 'has_java', 'has_sql', 'has_frontend', 'has_backend', 'has_cloud', 'has_docker', 'has_mobile'] if locals().get(f'has_{x}', 0) == 1]),
            'is_technical': 1 if locals().get('tech_skill_count', 0) >= 2 else 0,
            
            # Business keywords
            'has_sales': 1 if any(x in title_lower for x in ['sales', 'selling', 'business development', 'bd']) else 0,
            'has_marketing': 1 if any(x in title_lower for x in ['marketing', 'digital marketing', 'seo', 'social media', 'brand']) else 0,
            'has_accounting': 1 if any(x in title_lower for x in ['accountant', 'accounting', 'finance', 'cashier', 'audit', 'tax', 'bookkeeper']) else 0,
            'has_hr': 1 if any(x in title_lower for x in ['hr', 'human resources', 'recruitment', 'talent', 'people']) else 0,
            'has_admin': 1 if any(x in title_lower for x in ['admin', 'secretary', 'reception', 'office', 'assistant', 'clerical']) else 0,
            'has_manager': 1 if 'manager' in title_lower or 'management' in title_lower else 0,
            'has_supply': 1 if any(x in title_lower for x in ['logistics', 'supply chain', 'procurement', 'warehouse']) else 0,
            'has_customer': 1 if any(x in title_lower for x in ['customer service', 'support', 'client', 'call center']) else 0,
            'has_legal': 1 if any(x in title_lower for x in ['legal', 'law', 'attorney', 'paralegal', 'compliance']) else 0,
            'has_project': 1 if any(x in title_lower for x in ['project manager', 'program manager', 'scrum master', 'agile']) else 0,
            'has_product': 1 if any(x in title_lower for x in ['product manager', 'product owner', 'product specialist']) else 0,
            'business_skill_count': sum([1 for x in ['has_sales', 'has_marketing', 'has_accounting', 'has_hr', 'has_admin'] if locals().get(f'has_{x}', 0) == 1]),
            
            # Healthcare keywords
            'has_medical': 1 if any(x in title_lower for x in ['nurse', 'doctor', 'medical', 'health', 'clinical', 'patient', 'hospital', 'clinic']) else 0,
            'has_nursing': 1 if 'nurse' in title_lower or 'nursing' in title_lower or 'caregiver' in title_lower else 0,
            'has_pharmacy': 1 if any(x in title_lower for x in ['pharmacy', 'pharmacist', 'drug', 'medication']) else 0,
            'has_lab': 1 if any(x in title_lower for x in ['laboratory', 'lab', 'technician', 'radiology']) else 0,
            'has_doctor': 1 if any(x in title_lower for x in ['doctor', 'physician', 'surgeon', 'dentist']) else 0,
            'healthcare_skill_count': sum([1 for x in ['has_medical', 'has_nursing', 'has_pharmacy'] if locals().get(f'has_{x}', 0) == 1]),
            
            # Education keywords
            'has_teaching': 1 if any(x in title_lower for x in ['teacher', 'teaching', 'instructor', 'professor', 'lecturer', 'faculty']) else 0,
            'has_training': 1 if any(x in title_lower for x in ['trainer', 'training', 'coach', 'mentor', 'tutor']) else 0,
            'has_education': 1 if any(x in title_lower for x in ['education', 'school', 'university', 'college', 'academy']) else 0,
            'has_curriculum': 1 if any(x in title_lower for x in ['curriculum', 'syllabus', 'lesson', 'course']) else 0,
            
            # Job type features
            'is_remote': 1 if 'remote' in job_type.lower() or 'work from home' in job_type.lower() else 0,
            'is_hybrid': 1 if 'hybrid' in job_type.lower() else 0,
            'is_fulltime': 1 if 'full' in job_type.lower() or 'permanent' in job_type.lower() else 0,
            'is_parttime': 1 if 'part' in job_type.lower() or 'hourly' in job_type.lower() or 'temporary' in job_type.lower() else 0,
            'is_contract': 1 if 'contract' in job_type.lower() or 'consultant' in job_type.lower() else 0,
            'is_freelance': 1 if 'freelance' in job_type.lower() or 'gig' in job_type.lower() else 0,
            
            # Sector features
            'is_tech_sector': 1 if 'technology' in str(sector).lower() or 'it' in str(sector).lower() or 'software' in str(sector).lower() else 0,
            'is_finance_sector': 1 if 'finance' in str(sector).lower() or 'bank' in str(sector).lower() or 'insurance' in str(sector).lower() else 0,
            'is_health_sector': 1 if 'health' in str(sector).lower() or 'medical' in str(sector).lower() or 'healthcare' in str(sector).lower() else 0,
            'is_education_sector': 1 if 'education' in str(sector).lower() or 'school' in str(sector).lower() or 'training' in str(sector).lower() else 0,
            'is_business_sector': 1 if 'business' in str(sector).lower() or 'consulting' in str(sector).lower() else 0,
            'is_engineering_sector': 1 if 'engineering' in str(sector).lower() or 'construction' in str(sector).lower() else 0,
            'is_agriculture_sector': 1 if 'agriculture' in str(sector).lower() or 'farming' in str(sector).lower() else 0,
            'sector_confidence': (1 if 'technology' in str(sector).lower() else 0) * 3 + (1 if 'finance' in str(sector).lower() else 0) * 3,
            
            # Location features
            'is_addis': 1 if 'addis' in location.lower() else 0,
            'is_remote_location': 1 if 'remote' in location.lower() or 'anywhere' in location.lower() else 0,
            'is_regional': 1 if any(x in location.lower() for x in ['oromia', 'amhara', 'tigray', 'hawassa', 'bahir', 'adama']) else 0,
            'location_score': (1 if 'addis' in location.lower() else 0) * 2 + (1 if 'remote' in location.lower() else 0) * 1,
            
            # Experience features
            'exp_senior': 1 if 'senior' in experience.lower() or '5+' in experience or 'expert' in experience.lower() else 0,
            'exp_mid': 1 if 'mid' in experience.lower() or '3-5' in experience or 'intermediate' in experience.lower() else 0,
            'exp_entry': 1 if 'entry' in experience.lower() or 'junior' in experience.lower() or '1-2' in experience or 'fresh' in experience.lower() else 0,
            'exp_years_1_3': 1 if '1-3' in experience or '1-2' in experience else 0,
            'exp_years_3_5': 1 if '3-5' in experience or '3-4' in experience else 0,
            'exp_years_5_plus': 1 if '5+' in experience or '5-10' in experience or '10+' in experience else 0,
            
            # Description features
            'desc_length': min(len(description), 500) if description else 0,
            'desc_word_count': len(description.split()) if description else 0,
            'desc_has_tech': 1 if any(x in description.lower() for x in ['python', 'javascript', 'java', 'react', 'aws', 'docker']) if description else 0,
            'desc_has_business': 1 if any(x in description.lower() for x in ['sales', 'marketing', 'client', 'customer', 'revenue']) if description else 0,
            'desc_quality_score': min(len(description) / 200, 1) if description else 0,
        }
        
        return pd.DataFrame([feature])
    
    def predict(self, job_title, job_type='', sector='', location='', experience='', description=''):
        """Predict job category with confidence"""
        X = self.extract_features(job_title, job_type, sector, location, experience, description)
        X_scaled = self.scaler.transform(X)
        probabilities = self.rf_model.predict_proba(X_scaled)[0]
        
        prediction = np.argmax(probabilities)
        category = self.encoder.inverse_transform([prediction])[0]
        confidence = max(probabilities) * 100
        
        all_probs = {}
        for i, prob in enumerate(probabilities):
            cat = self.encoder.inverse_transform([i])[0]
            all_probs[cat] = round(prob * 100, 1)
        
        # Apply business rules for correction
        title_lower = job_title.lower()
        
        # Rule: Developer/Engineer titles should be Technology
        if any(x in title_lower for x in ['developer', 'engineer', 'programmer', 'software', 'coder', 'python', 'java', 'javascript']):
            if category != 'Technology':
                category = 'Technology'
                confidence = max(confidence, 75)
        
        # Rule: Finance titles should be Finance
        if any(x in title_lower for x in ['accountant', 'finance', 'cashier', 'audit', 'tax', 'bookkeeper']):
            if category != 'Finance':
                category = 'Finance'
                confidence = max(confidence, 80)
        
        # Rule: Healthcare titles should be Healthcare
        if any(x in title_lower for x in ['nurse', 'doctor', 'medical', 'clinical']):
            if category != 'Healthcare':
                category = 'Healthcare'
                confidence = max(confidence, 80)
        
        # Rule: Education titles should be Education
        if any(x in title_lower for x in ['teacher', 'instructor', 'professor', 'lecturer']):
            if category != 'Education':
                category = 'Education'
                confidence = max(confidence, 80)
        
        return {
            'category': category,
            'confidence': round(confidence, 1),
            'all_probabilities': all_probs,
            'model_used': 'Enhanced Random Forest (60+ features)'
        }

# Create global instance
enhanced_predictor = EnhancedJobPredictor()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTING ENHANCED PREDICTOR")
    print("="*60)
    
    test_jobs = [
        "Senior Python Developer",
        "Accountant",
        "Sales Manager", 
        "Nurse",
        "Teacher",
        "Software Engineer",
        "DevOps Engineer",
        "Data Scientist",
        "HR Officer",
        "Project Manager"
    ]
    
    for job in test_jobs:
        result = enhanced_predictor.predict(job)
        print(f"\n📌 '{job}'")
        print(f"   → Predicted: {result['category']} (Confidence: {result['confidence']}%)")
        print(f"   → Top 3: {sorted(result['all_probabilities'].items(), key=lambda x: x[1], reverse=True)[:3]}")