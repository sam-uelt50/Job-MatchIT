# backend/random_forest_matcher.py
import pandas as pd
import numpy as np
import pickle
import os
import sqlite3
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, accuracy_score, classification_report
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class RandomForestJobMatcher:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoders = {}
        self.feature_importance = None
        self.model_path = "ml_models/"
        
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)
        
        self.load_model()
    
    def load_model(self):
        """Load pre-trained Random Forest model"""
        try:
            with open(f"{self.model_path}random_forest_job_matcher.pkl", "rb") as f:
                self.model = pickle.load(f)
            with open(f"{self.model_path}random_forest_scaler.pkl", "rb") as f:
                self.scaler = pickle.load(f)
            with open(f"{self.model_path}random_forest_encoders.pkl", "rb") as f:
                self.label_encoders = pickle.load(f)
            print("✅ Random Forest model loaded")
            return True
        except:
            print("⚠️ No existing Random Forest model found")
            return False
    
    def save_model(self):
        """Save trained model"""
        with open(f"{self.model_path}random_forest_job_matcher.pkl", "wb") as f:
            pickle.dump(self.model, f)
        with open(f"{self.model_path}random_forest_scaler.pkl", "wb") as f:
            pickle.dump(self.scaler, f)
        with open(f"{self.model_path}random_forest_encoders.pkl", "wb") as f:
            pickle.dump(self.label_encoders, f)
        print("✅ Random Forest model saved")
    
    def prepare_training_data(self):
        """Prepare data from Afriwork dataset for training"""
        import pandas as pd
        
        # Load Afriwork dataset
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'afriwork.csv')
        
        if not os.path.exists(csv_path):
            print(f"❌ Dataset not found: {csv_path}")
            return None
        
        df = pd.read_csv(csv_path)
        print(f"📊 Loaded {len(df)} records for training")
        
        # Create features from available columns
        features = []
        targets = []
        
        # Process each row
        for idx, row in df.iterrows():
            # Extract features
            job_title = str(row.get('Job_title', ''))
            job_type = str(row.get('Job_type', ''))
            sector = str(row.get('sector', ''))
            location = str(row.get('location', ''))
            experience = str(row.get('Experience_level', ''))
            
            # Create feature vector
            feature = {
                'title_length': len(job_title),
                'has_remote': 1 if 'remote' in job_type.lower() else 0,
                'has_fulltime': 1 if 'full' in job_type.lower() else 0,
                'sector_tech': 1 if 'technology' in sector.lower() else 0,
                'sector_health': 1 if 'health' in sector.lower() else 0,
                'sector_finance': 1 if 'finance' in sector.lower() else 0,
                'is_addis': 1 if 'addis' in location.lower() else 0,
                'is_remote_location': 1 if 'remote' in location.lower() else 0,
                'senior_level': 1 if 'senior' in experience.lower() else 0,
                'entry_level': 1 if 'entry' in experience.lower() or 'junior' in experience.lower() else 0,
                'mid_level': 1 if 'mid' in experience.lower() or 'intermediate' in experience.lower() else 0,
            }
            
            features.append(feature)
            
            # Create target (job category based on title)
            title_lower = job_title.lower()
            if 'developer' in title_lower or 'engineer' in title_lower or 'programmer' in title_lower:
                target = 'Technology'
            elif 'accountant' in title_lower or 'finance' in title_lower or 'cashier' in title_lower:
                target = 'Finance'
            elif 'teacher' in title_lower or 'instructor' in title_lower or 'professor' in title_lower:
                target = 'Education'
            elif 'nurse' in title_lower or 'doctor' in title_lower or 'medical' in title_lower:
                target = 'Healthcare'
            elif 'sales' in title_lower or 'marketing' in title_lower or 'manager' in title_lower:
                target = 'Business'
            else:
                target = 'General'
            
            targets.append(target)
        
        # Convert to DataFrame
        X = pd.DataFrame(features)
        y = pd.Series(targets)
        
        print(f"✅ Prepared {len(X)} training samples")
        print(f"📊 Feature columns: {list(X.columns)}")
        print(f"🎯 Target distribution:\n{y.value_counts()}")
        
        return X, y
    
    def train_model(self):
        """Train Random Forest model"""
        print("=" * 60)
        print("🌲 Training Random Forest Job Matcher")
        print("=" * 60)
        
        # Prepare data
        data = self.prepare_training_data()
        if data is None:
            return False
        
        X, y = data
        
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
        
        # Train Random Forest Classifier
        self.model = RandomForestClassifier(
            n_estimators=100,        # Number of trees
            max_depth=15,            # Maximum depth
            min_samples_split=10,    # Minimum samples to split
            min_samples_leaf=5,      # Minimum samples at leaf
            random_state=42,
            n_jobs=-1,               # Use all CPU cores
            class_weight='balanced'  # Handle imbalanced classes
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n📊 Model Performance:")
        print(f"   Accuracy: {accuracy:.3f}")
        print(f"   Training samples: {len(X_train)}")
        print(f"   Test samples: {len(X_test)}")
        
        # Feature importance
        self.feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n📈 Feature Importance:")
        for _, row in self.feature_importance.head(10).iterrows():
            print(f"   {row['feature']}: {row['importance']:.3f}")
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_scaled, y_encoded, cv=5)
        print(f"\n🔬 Cross-validation scores: {cv_scores}")
        print(f"   Mean CV accuracy: {cv_scores.mean():.3f}")
        
        # Save model
        self.save_model()
        
        return True
    
    def predict_job_category(self, job_title, job_type, sector, location, experience):
        """Predict job category using Random Forest"""
        if self.model is None:
            return None
        
        # Create feature vector
        features = [{
            'title_length': len(str(job_title)),
            'has_remote': 1 if 'remote' in str(job_type).lower() else 0,
            'has_fulltime': 1 if 'full' in str(job_type).lower() else 0,
            'sector_tech': 1 if 'technology' in str(sector).lower() else 0,
            'sector_health': 1 if 'health' in str(sector).lower() else 0,
            'sector_finance': 1 if 'finance' in str(sector).lower() else 0,
            'is_addis': 1 if 'addis' in str(location).lower() else 0,
            'is_remote_location': 1 if 'remote' in str(location).lower() else 0,
            'senior_level': 1 if 'senior' in str(experience).lower() else 0,
            'entry_level': 1 if 'entry' in str(experience).lower() or 'junior' in str(experience).lower() else 0,
            'mid_level': 1 if 'mid' in str(experience).lower() or 'intermediate' in str(experience).lower() else 0,
        }]
        
        # Scale features
        X = pd.DataFrame(features)
        X_scaled = self.scaler.transform(X)
        
        # Predict
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]
        
        # Get class names
        class_names = self.label_encoders['target'].classes_
        prediction_label = class_names[prediction]
        
        # Get confidence
        confidence = max(probabilities) * 100
        
        # Get top 3 predictions
        top_3_indices = probabilities.argsort()[-3:][::-1]
        top_3_predictions = [
            {'category': class_names[idx], 'confidence': round(probabilities[idx] * 100, 1)}
            for idx in top_3_indices
        ]
        
        return {
            'predicted_category': prediction_label,
            'confidence': round(confidence, 1),
            'top_predictions': top_3_predictions,
            'feature_importance': self.feature_importance.to_dict('records') if self.feature_importance is not None else None
        }
    
    def calculate_match_score_rf(self, user_skills, user_exp, job_skills, job_exp_req, 
                                   job_title, job_type, sector, location):
        """Calculate enhanced match score using Random Forest"""
        
        # Get category prediction
        category_result = self.predict_job_category(job_title, job_type, sector, location, f"{job_exp_req}+ years")
        
        if category_result is None:
            return None
        
        # Base skill match (50% of score)
        job_skills_lower = [s.lower() for s in job_skills]
        user_skills_lower = [s.lower() for s in user_skills]
        
        if job_skills_lower:
            matched = sum(1 for js in job_skills_lower if js in user_skills_lower)
            skill_score = (matched / len(job_skills_lower)) * 100
        else:
            skill_score = 0
        
        # Experience match (25% of score)
        if user_exp >= job_exp_req:
            exp_score = 100
        elif user_exp > 0:
            exp_score = (user_exp / job_exp_req) * 100
        else:
            exp_score = 0
        
        # Random Forest category match (25% of score)
        rf_score = category_result['confidence']
        
        # Calculate final score
        final_score = (skill_score * 0.50) + (exp_score * 0.25) + (rf_score * 0.25)
        final_score = min(100, max(0, round(final_score)))
        
        # Determine category
        if final_score >= 85:
            match_level = "🏆 Excellent Match"
            color = "#28a745"
        elif final_score >= 70:
            match_level = "⭐ Great Match"
            color = "#17a2b8"
        elif final_score >= 55:
            match_level = "👍 Good Match"
            color = "#ffc107"
        elif final_score >= 40:
            match_level = "📌 Potential Match"
            color = "#fd7e14"
        else:
            match_level = "⚠️ Low Match"
            color = "#dc3545"
        
        return {
            'match_score': final_score,
            'match_level': match_level,
            'color': color,
            'skill_score': round(skill_score, 1),
            'exp_score': round(exp_score, 1),
            'rf_score': rf_score,
            'predicted_category': category_result['predicted_category'],
            'rf_confidence': category_result['confidence'],
            'top_predictions': category_result['top_predictions']
        }

# Initialize global instance
rf_matcher = RandomForestJobMatcher()