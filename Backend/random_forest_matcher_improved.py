# backend/random_forest_matcher_improved.py
import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

class ImprovedRandomForestMatcher:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoders = {}
        self.model_path = "ml_models/"
        
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)
        
        self.load_model()
    
    def load_model(self):
        try:
            with open(f"{self.model_path}improved_random_forest.pkl", "rb") as f:
                self.model = pickle.load(f)
            with open(f"{self.model_path}improved_rf_scaler.pkl", "rb") as f:
                self.scaler = pickle.load(f)
            with open(f"{self.model_path}improved_rf_encoders.pkl", "rb") as f:
                self.label_encoders = pickle.load(f)
            print("✅ Improved Random Forest model loaded")
            return True
        except:
            print("⚠️ No existing model found")
            return False
    
    def save_model(self):
        with open(f"{self.model_path}improved_random_forest.pkl", "wb") as f:
            pickle.dump(self.model, f)
        with open(f"{self.model_path}improved_rf_scaler.pkl", "wb") as f:
            pickle.dump(self.scaler, f)
        with open(f"{self.model_path}improved_rf_encoders.pkl", "wb") as f:
            pickle.dump(self.label_encoders, f)
        print("✅ Improved model saved")
    
    def extract_skills_from_title(self, title):
        """Extract skills from job title"""
        skills = []
        title_lower = title.lower()
        skill_keywords = {
            'python': ['python', 'django', 'flask'],
            'javascript': ['javascript', 'js', 'react', 'angular', 'vue', 'node'],
            'java': ['java', 'spring'],
            'data': ['data', 'analytics', 'bi'],
            'cloud': ['aws', 'azure', 'cloud', 'devops'],
            'database': ['sql', 'database', 'mongodb', 'postgres']
        }
        
        for category, keywords in skill_keywords.items():
            for kw in keywords:
                if kw in title_lower:
                    skills.append(category)
                    break
        return skills
    
    def prepare_enhanced_training_data(self):
        import pandas as pd
        
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'afriwork.csv')
        
        if not os.path.exists(csv_path):
            print(f"❌ Dataset not found: {csv_path}")
            return None
        
        df = pd.read_csv(csv_path)
        print(f"📊 Loaded {len(df)} records")
        
        features = []
        targets = []
        
        for idx, row in df.iterrows():
            if idx > 5000:
                break
                
            job_title = str(row.get('Job_title', ''))
            job_type = str(row.get('Job_type', ''))
            sector = str(row.get('sector', ''))
            location = str(row.get('location', ''))
            experience = str(row.get('Experience_level', ''))
            description = str(row.get('description', ''))
            
            if not job_title or job_title == 'nan':
                continue
            
            # Extract skills from title
            skills = self.extract_skills_from_title(job_title)
            
            # Create rich feature set
            feature = {
                # Title features
                'title_length': min(len(job_title), 50),
                'has_senior': 1 if 'senior' in job_title.lower() else 0,
                'has_junior': 1 if 'junior' in job_title.lower() else 0,
                'has_lead': 1 if 'lead' in job_title.lower() or 'manager' in job_title.lower() else 0,
                
                # Skill features
                'has_python': 1 if 'python' in job_title.lower() or 'django' in job_title.lower() else 0,
                'has_javascript': 1 if any(x in job_title.lower() for x in ['javascript', 'react', 'angular', 'node']) else 0,
                'has_java': 1 if 'java' in job_title.lower() else 0,
                'has_data': 1 if any(x in job_title.lower() for x in ['data', 'analytics', 'bi']) else 0,
                'has_cloud': 1 if any(x in job_title.lower() for x in ['aws', 'cloud', 'devops']) else 0,
                'skill_count': len(skills),
                
                # Job type features
                'is_remote': 1 if 'remote' in job_type.lower() else 0,
                'is_fulltime': 1 if 'full' in job_type.lower() else 0,
                'is_contract': 1 if 'contract' in job_type.lower() else 0,
                'is_parttime': 1 if 'part' in job_type.lower() else 0,
                
                # Sector features
                'is_tech': 1 if 'technology' in sector.lower() or 'it' in sector.lower() else 0,
                'is_health': 1 if 'health' in sector.lower() or 'medical' in sector.lower() else 0,
                'is_finance': 1 if 'finance' in sector.lower() or 'bank' in sector.lower() else 0,
                'is_education': 1 if 'education' in sector.lower() or 'teaching' in sector.lower() else 0,
                'is_business': 1 if 'business' in sector.lower() or 'sales' in sector.lower() or 'marketing' in sector.lower() else 0,
                
                # Location features
                'is_addis': 1 if 'addis' in location.lower() else 0,
                'is_remote_loc': 1 if 'remote' in location.lower() else 0,
                
                # Experience features
                'exp_senior': 1 if 'senior' in experience.lower() else 0,
                'exp_mid': 1 if 'mid' in experience.lower() or 'intermediate' in experience.lower() else 0,
                'exp_entry': 1 if 'entry' in experience.lower() or 'junior' in experience.lower() else 0,
                
                # Description features
                'desc_length': min(len(description), 200) if description else 0,
            }
            
            features.append(feature)
            
            # Determine target category
            title_lower = job_title.lower()
            if any(word in title_lower for word in ['developer', 'engineer', 'programmer', 'software', 'it', 'tech', 'python', 'javascript', 'java', 'react', 'angular']):
                target = 'Technology'
            elif any(word in title_lower for word in ['accountant', 'finance', 'cashier', 'audit', 'bank', 'financial', 'accounting']):
                target = 'Finance'
            elif any(word in title_lower for word in ['teacher', 'instructor', 'professor', 'trainer', 'educator', 'school', 'teaching']):
                target = 'Education'
            elif any(word in title_lower for word in ['nurse', 'doctor', 'medical', 'health', 'clinic', 'hospital', 'healthcare']):
                target = 'Healthcare'
            elif any(word in title_lower for word in ['sales', 'marketing', 'manager', 'business', 'hr', 'human resources', 'administration']):
                target = 'Business'
            else:
                target = 'General'
            
            targets.append(target)
        
        if not features:
            print("❌ No valid features extracted")
            return None
        
        X = pd.DataFrame(features)
        y = pd.Series(targets)
        
        print(f"✅ Prepared {len(X)} training samples")
        print(f"📊 Features: {len(X.columns)}")
        print(f"🎯 Target distribution:\n{y.value_counts()}")
        
        return X, y
    
    def train_model(self):
        print("=" * 60)
        print("🌲 Training IMPROVED Random Forest Model")
        print("=" * 60)
        
        data = self.prepare_enhanced_training_data()
        if data is None:
            return False
        
        X, y = data
        
        if len(X) < 100:
            print("❌ Not enough training data")
            return False
        
        # Encode target
        target_encoder = LabelEncoder()
        y_encoded = target_encoder.fit_transform(y)
        self.label_encoders['target'] = target_encoder
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Train with better parameters
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n📊 Model Performance:")
        print(f"   Accuracy: {accuracy:.3f}")
        print(f"   Training samples: {len(X_train)}")
        print(f"   Test samples: {len(X_test)}")
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_scaled, y_encoded, cv=5)
        print(f"   Cross-validation scores: {cv_scores}")
        print(f"   Mean CV: {cv_scores.mean():.3f}")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n📈 Top 10 Feature Importance:")
        for _, row in feature_importance.head(10).iterrows():
            print(f"   {row['feature']}: {row['importance']:.3f}")
        
        self.save_model()
        return True
    
    def predict_category(self, job_title, job_type, sector, location, experience):
        """Predict job category"""
        if self.model is None:
            return None
        
        skills = self.extract_skills_from_title(job_title)
        
        features = [{
            'title_length': min(len(job_title), 50),
            'has_senior': 1 if 'senior' in job_title.lower() else 0,
            'has_junior': 1 if 'junior' in job_title.lower() else 0,
            'has_lead': 1 if 'lead' in job_title.lower() or 'manager' in job_title.lower() else 0,
            'has_python': 1 if 'python' in job_title.lower() else 0,
            'has_javascript': 1 if any(x in job_title.lower() for x in ['javascript', 'react', 'angular', 'node']) else 0,
            'has_java': 1 if 'java' in job_title.lower() else 0,
            'has_data': 1 if any(x in job_title.lower() for x in ['data', 'analytics']) else 0,
            'has_cloud': 1 if any(x in job_title.lower() for x in ['aws', 'cloud', 'devops']) else 0,
            'skill_count': len(skills),
            'is_remote': 1 if 'remote' in job_type.lower() else 0,
            'is_fulltime': 1 if 'full' in job_type.lower() else 0,
            'is_contract': 1 if 'contract' in job_type.lower() else 0,
            'is_parttime': 1 if 'part' in job_type.lower() else 0,
            'is_tech': 1 if 'technology' in sector.lower() or 'it' in sector.lower() else 0,
            'is_health': 1 if 'health' in sector.lower() else 0,
            'is_finance': 1 if 'finance' in sector.lower() else 0,
            'is_education': 1 if 'education' in sector.lower() else 0,
            'is_business': 1 if 'business' in sector.lower() else 0,
            'is_addis': 1 if 'addis' in location.lower() else 0,
            'is_remote_loc': 1 if 'remote' in location.lower() else 0,
            'exp_senior': 1 if 'senior' in experience.lower() else 0,
            'exp_mid': 1 if 'mid' in experience.lower() else 0,
            'exp_entry': 1 if 'entry' in experience.lower() or 'junior' in experience.lower() else 0,
            'desc_length': 100,
        }]
        
        X = pd.DataFrame(features)
        X_scaled = self.scaler.transform(X)
        
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]
        
        class_names = self.label_encoders['target'].classes_
        predicted_category = class_names[prediction]
        confidence = max(probabilities) * 100
        
        return {
            'category': predicted_category,
            'confidence': round(confidence, 1),
            'all_probabilities': {class_names[i]: round(probabilities[i] * 100, 1) for i in range(len(class_names))}
        }

# Create instance
improved_rf = ImprovedRandomForestMatcher()