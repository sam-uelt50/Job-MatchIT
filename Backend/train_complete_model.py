# backend/train_complete_model.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle
import os
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("🌲🌲🌲 COMPLETE RANDOM FOREST TRAINING - ALL 41,953 RECORDS 🌲🌲🌲")
print("=" * 80)

# Load full dataset
csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'afriwork.csv')
df = pd.read_csv(csv_path)
print(f"\n📊 Loaded {len(df):,} total records")
print(f"✅ Using ALL {len(df):,} records for training (NO LIMITS)")

features = []
targets = []
skipped = 0
error_count = 0

# Process ALL rows - NO LIMITS
print("\n🔧 Processing all records...")

for idx, row in df.iterrows():
    try:
        job_title = str(row.get('Job_title', ''))
        job_type = str(row.get('Job_type', ''))
        sector = str(row.get('sector', ''))
        location = str(row.get('location', ''))
        experience = str(row.get('Experience_level', ''))
        description = str(row.get('description', ''))
        
        if not job_title or job_title == 'nan' or len(job_title) < 2:
            skipped += 1
            continue
        
        # COMPREHENSIVE FEATURE SET - 45+ FEATURES
        feature = {
            # === TITLE FEATURES (12 features) ===
            'title_length': min(len(job_title), 150),
            'title_word_count': len(job_title.split()),
            'has_senior': 1 if 'senior' in job_title.lower() else 0,
            'has_junior': 1 if 'junior' in job_title.lower() or 'entry' in job_title.lower() else 0,
            'has_lead': 1 if any(x in job_title.lower() for x in ['lead', 'manager', 'director', 'head', 'supervisor', 'chief']) else 0,
            'has_intern': 1 if 'intern' in job_title.lower() or 'trainee' in job_title.lower() else 0,
            'has_assistant': 1 if 'assistant' in job_title.lower() or 'aide' in job_title.lower() else 0,
            'has_specialist': 1 if 'specialist' in job_title.lower() or 'expert' in job_title.lower() else 0,
            'has_officer': 1 if 'officer' in job_title.lower() else 0,
            'has_coordinator': 1 if 'coordinator' in job_title.lower() else 0,
            'has_consultant': 1 if 'consultant' in job_title.lower() or 'advisor' in job_title.lower() else 0,
            'has_technician': 1 if 'technician' in job_title.lower() or 'operator' in job_title.lower() else 0,
            
            # === PROGRAMMING LANGUAGES (10 features) ===
            'has_python': 1 if any(x in job_title.lower() for x in ['python', 'django', 'flask', 'fastapi']) else 0,
            'has_javascript': 1 if any(x in job_title.lower() for x in ['javascript', 'js', 'react', 'angular', 'vue', 'node', 'express']) else 0,
            'has_java': 1 if any(x in job_title.lower() for x in ['java', 'spring', 'kotlin', 'j2ee']) else 0,
            'has_cpp': 1 if any(x in job_title.lower() for x in ['c++', 'cpp', 'c#', 'csharp', '.net']) else 0,
            'has_php': 1 if 'php' in job_title.lower() or 'laravel' in job_title.lower() else 0,
            'has_ruby': 1 if 'ruby' in job_title.lower() or 'rails' in job_title.lower() else 0,
            'has_go': 1 if 'golang' in job_title.lower() or 'go ' in job_title.lower() else 0,
            'has_rust': 1 if 'rust' in job_title.lower() else 0,
            'has_swift': 1 if 'swift' in job_title.lower() or 'ios' in job_title.lower() else 0,
            'has_kotlin': 1 if 'kotlin' in job_title.lower() or 'android' in job_title.lower() else 0,
            
            # === FRAMEWORKS & TECHNOLOGIES (10 features) ===
            'has_react': 1 if 'react' in job_title.lower() or 'next' in job_title.lower() else 0,
            'has_angular': 1 if 'angular' in job_title.lower() or 'vue' in job_title.lower() else 0,
            'has_django': 1 if 'django' in job_title.lower() or 'flask' in job_title.lower() else 0,
            'has_spring': 1 if 'spring' in job_title.lower() or 'hibernate' in job_title.lower() else 0,
            'has_node': 1 if 'node' in job_title.lower() or 'express' in job_title.lower() else 0,
            'has_docker': 1 if any(x in job_title.lower() for x in ['docker', 'kubernetes', 'k8s', 'container']) else 0,
            'has_aws': 1 if any(x in job_title.lower() for x in ['aws', 'amazon', 'ec2', 's3', 'lambda', 'cloud']) else 0,
            'has_azure': 1 if any(x in job_title.lower() for x in ['azure', 'microsoft cloud', 'gcp', 'google cloud']) else 0,
            'has_jenkins': 1 if any(x in job_title.lower() for x in ['jenkins', 'ci/cd', 'gitlab', 'github actions']) else 0,
            'has_terraform': 1 if any(x in job_title.lower() for x in ['terraform', 'ansible', 'puppet', 'chef']) else 0,
            
            # === DATABASE SKILLS (5 features) ===
            'has_sql': 1 if any(x in job_title.lower() for x in ['sql', 'mysql', 'postgresql', 'postgres']) else 0,
            'has_mongodb': 1 if any(x in job_title.lower() for x in ['mongodb', 'mongo', 'nosql']) else 0,
            'has_redis': 1 if 'redis' in job_title.lower() or 'cache' in job_title.lower() else 0,
            'has_oracle': 1 if 'oracle' in job_title.lower() or 'pl/sql' in job_title.lower() else 0,
            'has_database': 1 if any(x in job_title.lower() for x in ['database', 'dba', 'data warehouse']) else 0,
            
            # === DATA SCIENCE & AI (6 features) ===
            'has_machine_learning': 1 if any(x in job_title.lower() for x in ['machine learning', 'ml', 'deep learning', 'dl']) else 0,
            'has_ai': 1 if any(x in job_title.lower() for x in ['artificial intelligence', 'ai', 'nlp', 'computer vision']) else 0,
            'has_tensorflow': 1 if any(x in job_title.lower() for x in ['tensorflow', 'pytorch', 'keras', 'scikit-learn']) else 0,
            'has_data_science': 1 if any(x in job_title.lower() for x in ['data science', 'data scientist', 'analytics']) else 0,
            'has_pandas': 1 if any(x in job_title.lower() for x in ['pandas', 'numpy', 'matplotlib']) else 0,
            'has_big_data': 1 if any(x in job_title.lower() for x in ['big data', 'hadoop', 'spark', 'kafka']) else 0,
            
            # === BUSINESS & SOFT SKILLS (8 features) ===
            'has_sales': 1 if any(x in job_title.lower() for x in ['sales', 'selling', 'business development', 'bd']) else 0,
            'has_marketing': 1 if any(x in job_title.lower() for x in ['marketing', 'digital marketing', 'seo', 'social media']) else 0,
            'has_finance': 1 if any(x in job_title.lower() for x in ['finance', 'accounting', 'accountant', 'audit', 'tax', 'budget']) else 0,
            'has_hr': 1 if any(x in job_title.lower() for x in ['hr', 'human resources', 'recruitment', 'talent', 'people']) else 0,
            'has_admin': 1 if any(x in job_title.lower() for x in ['admin', 'administrative', 'office', 'secretary', 'reception']) else 0,
            'has_customer': 1 if any(x in job_title.lower() for x in ['customer service', 'support', 'client', 'call center']) else 0,
            'has_communication': 1 if any(x in job_title.lower() for x in ['communication', 'interpersonal', 'presentation']) else 0,
            'has_leadership': 1 if any(x in job_title.lower() for x in ['leadership', 'team lead', 'team management']) else 0,
            
            # === HEALTHCARE SKILLS (5 features) ===
            'has_medical': 1 if any(x in job_title.lower() for x in ['medical', 'health', 'clinical', 'patient', 'hospital', 'clinic']) else 0,
            'has_nursing': 1 if any(x in job_title.lower() for x in ['nurse', 'nursing', 'caregiver', 'caretaker']) else 0,
            'has_doctor': 1 if any(x in job_title.lower() for x in ['doctor', 'physician', 'surgeon', 'dentist']) else 0,
            'has_pharmacy': 1 if any(x in job_title.lower() for x in ['pharmacy', 'pharmacist', 'drug', 'medication']) else 0,
            'has_lab': 1 if any(x in job_title.lower() for x in ['laboratory', 'lab', 'technician', 'radiology']) else 0,
            
            # === EDUCATION SKILLS (4 features) ===
            'has_teaching': 1 if any(x in job_title.lower() for x in ['teacher', 'teaching', 'instructor', 'professor', 'lecturer', 'faculty']) else 0,
            'has_training': 1 if any(x in job_title.lower() for x in ['trainer', 'training', 'coach', 'mentor', 'tutor']) else 0,
            'has_education': 1 if any(x in job_title.lower() for x in ['education', 'educational', 'academic', 'school', 'university']) else 0,
            'has_curriculum': 1 if any(x in job_title.lower() for x in ['curriculum', 'syllabus', 'lesson', 'course']) else 0,
            
            # === ENGINEERING SKILLS (5 features) ===
            'has_civil': 1 if any(x in job_title.lower() for x in ['civil', 'construction', 'building', 'architecture']) else 0,
            'has_electrical': 1 if any(x in job_title.lower() for x in ['electrical', 'electronics', 'circuit', 'power']) else 0,
            'has_mechanical': 1 if any(x in job_title.lower() for x in ['mechanical', 'machinery', 'automotive', 'vehicle']) else 0,
            'has_industrial': 1 if any(x in job_title.lower() for x in ['industrial', 'manufacturing', 'production', 'factory']) else 0,
            'has_chemical': 1 if any(x in job_title.lower() for x in ['chemical', 'process', 'petroleum', 'oil']) else 0,
            
            # === JOB TYPE FEATURES (6 features) ===
            'is_remote': 1 if 'remote' in job_type.lower() or 'work from home' in job_type.lower() else 0,
            'is_hybrid': 1 if 'hybrid' in job_type.lower() else 0,
            'is_fulltime': 1 if 'full' in job_type.lower() or 'permanent' in job_type.lower() else 0,
            'is_parttime': 1 if 'part' in job_type.lower() or 'hourly' in job_type.lower() else 0,
            'is_contract': 1 if 'contract' in job_type.lower() or 'temporary' in job_type.lower() else 0,
            'is_freelance': 1 if 'freelance' in job_type.lower() or 'gig' in job_type.lower() else 0,
            
            # === SECTOR FEATURES (10 features) ===
            'sector_technology': 1 if any(x in sector.lower() for x in ['technology', 'it', 'software', 'tech', 'computer', 'information technology']) else 0,
            'sector_finance': 1 if any(x in sector.lower() for x in ['finance', 'bank', 'insurance', 'accounting', 'investment']) else 0,
            'sector_healthcare': 1 if any(x in sector.lower() for x in ['health', 'medical', 'healthcare', 'hospital', 'clinic', 'pharmaceutical']) else 0,
            'sector_education': 1 if any(x in sector.lower() for x in ['education', 'school', 'university', 'college', 'training', 'academy']) else 0,
            'sector_business': 1 if any(x in sector.lower() for x in ['business', 'consulting', 'management', 'administration']) else 0,
            'sector_engineering': 1 if any(x in sector.lower() for x in ['engineering', 'construction', 'civil', 'mechanical', 'electrical']) else 0,
            'sector_agriculture': 1 if any(x in sector.lower() for x in ['agriculture', 'farming', 'agri', 'crop', 'livestock']) else 0,
            'sector_manufacturing': 1 if any(x in sector.lower() for x in ['manufacturing', 'production', 'factory', 'industrial']) else 0,
            'sector_telecom': 1 if any(x in sector.lower() for x in ['telecom', 'telecommunication', 'mobile', 'network', 'isp']) else 0,
            'sector_hospitality': 1 if any(x in sector.lower() for x in ['hospitality', 'hotel', 'tourism', 'restaurant', 'catering']) else 0,
            
            # === LOCATION FEATURES (6 features) ===
            'is_addis_ababa': 1 if 'addis' in location.lower() else 0,
            'is_remote_location': 1 if 'remote' in location.lower() or 'anywhere' in location.lower() else 0,
            'is_oromia': 1 if 'oromia' in location.lower() else 0,
            'is_amhara': 1 if 'amhara' in location.lower() else 0,
            'is_tigray': 1 if 'tigray' in location.lower() else 0,
            'is_snnpr': 1 if 'snnpr' in location.lower() or 'south' in location.lower() else 0,
            
            # === EXPERIENCE LEVEL FEATURES (5 features) ===
            'exp_senior': 1 if any(x in experience.lower() for x in ['senior', 'expert', 'lead', 'principal']) else 0,
            'exp_mid': 1 if any(x in experience.lower() for x in ['mid', 'intermediate', 'experienced']) else 0,
            'exp_entry': 1 if any(x in experience.lower() for x in ['entry', 'junior', 'fresh', 'graduate', 'intern']) else 0,
            'exp_years_1_3': 1 if '1-3' in experience or '1-2' in experience else 0,
            'exp_years_3_5': 1 if '3-5' in experience or '3-4' in experience else 0,
            
            # === DESCRIPTION FEATURES (4 features) ===
            'desc_length': min(len(description), 1000) if description else 0,
            'desc_word_count': len(description.split()) if description else 0,
            'desc_has_responsibilities': 1 if 'responsibilit' in description.lower() else 0,
            'desc_has_requirements': 1 if 'requirement' in description.lower() or 'qualification' in description.lower() else 0,
            
            # === DERIVED FEATURES (5 features) ===
            'tech_skill_count': sum([1 for x in ['has_python', 'has_javascript', 'has_java', 'has_react', 'has_angular', 'has_django', 'has_node', 'has_sql', 'has_aws'] if feature.get(x, 0) == 1]),
            'business_skill_count': sum([1 for x in ['has_sales', 'has_marketing', 'has_finance', 'has_hr', 'has_admin'] if feature.get(x, 0) == 1]),
            'seniority_score': (feature['has_senior'] * 3) + (feature['has_lead'] * 4) + (feature['exp_senior'] * 2) + (feature['has_manager'] * 3),
            'is_technical': 1 if feature['tech_skill_count'] >= 2 else 0,
            'is_business': 1 if feature['business_skill_count'] >= 2 else 0,
        }
        
        # Add missing 'has_manager' for seniority_score
        feature['has_manager'] = feature['has_lead']
        
        features.append(feature)
        
        # Determine target category with enhanced logic
        title_lower = job_title.lower()
        
        # Category keywords with weights
        categories = {
            'Technology': ['developer', 'engineer', 'programmer', 'software', 'it', 'tech', 'python', 'javascript', 'java', 
                          'react', 'angular', 'node', 'django', 'sql', 'database', 'aws', 'cloud', 'devops', 'frontend', 
                          'backend', 'full stack', 'mobile', 'android', 'ios', 'data scientist', 'machine learning', 'ai',
                          'systems', 'network', 'security', 'cyber', 'analyst', 'qa', 'testing', 'devops', 'sre'],
            
            'Finance': ['accountant', 'finance', 'cashier', 'audit', 'tax', 'bank', 'financial', 'accounting', 'bookkeeper', 
                       'credit', 'loan', 'investment', 'payroll', 'controller', 'treasury', 'risk', 'compliance'],
            
            'Healthcare': ['nurse', 'doctor', 'medical', 'health', 'clinical', 'patient', 'hospital', 'clinic', 'pharmacy', 
                          'pharmacist', 'caregiver', 'laboratory', 'lab tech', 'radiologist', 'therapist', 'dentist', 'veterinary'],
            
            'Education': ['teacher', 'instructor', 'professor', 'lecturer', 'trainer', 'educator', 'school', 'university', 
                         'college', 'academic', 'curriculum', 'tutor', 'principal', 'dean', 'librarian'],
            
            'Business': ['sales', 'marketing', 'manager', 'business', 'hr', 'human resources', 'recruitment', 'admin', 
                        'administrative', 'office', 'secretary', 'receptionist', 'customer service', 'support', 'operations',
                        'logistics', 'supply chain', 'procurement', 'purchasing', 'executive', 'director', 'vp'],
            
            'Engineering': ['civil', 'mechanical', 'electrical', 'construction', 'architect', 'structural', 'transportation',
                           'water', 'power', 'energy', 'manufacturing', 'production', 'industrial', 'chemical', 'process']
        }
        
        category_scores = {}
        for category, keywords in categories.items():
            score = sum(2 if kw in title_lower else 0 for kw in keywords)
            category_scores[category] = score
        
        # Add sector bonus
        for category in category_scores:
            sector_key = f'sector_{category.lower()}'
            if sector_key in feature and feature[sector_key]:
                category_scores[category] += 3
        
        max_score = max(category_scores.values())
        if max_score > 0:
            target = max(category_scores, key=category_scores.get)
        else:
            target = 'General'
        
        targets.append(target)
        
        # Progress indicator
        if (idx + 1) % 5000 == 0:
            print(f"   Processed {idx + 1:,} records...")
            
    except Exception as e:
        error_count += 1
        continue

print(f"\n✅ Processed {len(features):,} valid job records")
print(f"⚠️ Skipped: {skipped} invalid records")
print(f"❌ Errors: {error_count}")

# Create DataFrame
X = pd.DataFrame(features)
y = pd.Series(targets)

print(f"\n📊 Feature matrix shape: {X.shape}")
print(f"📋 Total features: {len(X.columns)}")
print(f"🎯 Target categories: {y.nunique()}")

print(f"\n🎯 Target distribution:")
for category, count in y.value_counts().items():
    pct = (count / len(y)) * 100
    bar = '█' * int(pct / 2)
    print(f"   {category:15} : {count:6,} ({pct:5.1f}%) {bar}")

# Encode target
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

print(f"\n📊 Data split:")
print(f"   Training: {len(X_train):,} samples ({len(X_train)/len(X)*100:.1f}%)")
print(f"   Test: {len(X_test):,} samples ({len(X_test)/len(X)*100:.1f}%)")

# Train Random Forest
print("\n🌲 Training Random Forest Classifier...")
print("   This may take 5-10 minutes...")

rf_model = RandomForestClassifier(
    n_estimators=500,
    max_depth=30,
    min_samples_split=5,
    min_samples_leaf=2,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1,
    class_weight='balanced',
    verbose=1
)

rf_model.fit(X_train, y_train)

# Evaluate
y_pred = rf_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n{'='*80}")
print(f"📊 MODEL PERFORMANCE")
print(f"{'='*80}")
print(f"   Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"   Training samples: {len(X_train):,}")
print(f"   Test samples: {len(X_test):,}")

# Cross-validation
print(f"\n📊 5-Fold Cross-Validation:")
cv_scores = cross_val_score(rf_model, X_scaled, y_encoded, cv=5, n_jobs=-1)
print(f"   Scores: {[f'{s:.3f}' for s in cv_scores]}")
print(f"   Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")

# Per-category accuracy
print(f"\n📊 Per-Category Performance:")
print(f"{'='*80}")
report = classification_report(y_test, y_pred, target_names=label_encoder.classes_, output_dict=True)
for category in label_encoder.classes_:
    if category in report:
        print(f"   {category:15} - Precision: {report[category]['precision']:.3f}, Recall: {report[category]['recall']:.3f}, F1: {report[category]['f1-score']:.3f}")

# Feature importance
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

print(f"\n📈 TOP 30 MOST IMPORTANT FEATURES:")
print(f"{'='*80}")
for i, row in feature_importance.head(30).iterrows():
    bar_length = int(row['importance'] * 60)
    bar = '█' * bar_length
    print(f"   {i+1:2d}. {row['feature']:25} : {row['importance']:.4f} {bar}")

# Save model and artifacts
model_path = "ml_models/"
if not os.path.exists(model_path):
    os.makedirs(model_path)

with open(f"{model_path}complete_random_forest.pkl", "wb") as f:
    pickle.dump(rf_model, f)
with open(f"{model_path}complete_scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)
with open(f"{model_path}complete_label_encoder.pkl", "wb") as f:
    pickle.dump(label_encoder, f)

print(f"\n{'='*80}")
print(f"🎉 COMPLETE MODEL TRAINING FINISHED!")
print(f"{'='*80}")
print(f"   ✅ Model saved to: {model_path}complete_random_forest.pkl")
print(f"   📊 Final Accuracy: {accuracy*100:.2f}%")
print(f"   🔧 Features used: {len(X.columns)}")
print(f"   📁 Training data: {len(X):,} records")
print(f"   🎯 Categories: {len(label_encoder.classes_)}")
print(f"{'='*80}")