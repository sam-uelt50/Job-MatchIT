# backend/train_robust_model.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os
import re
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("🌲 ROBUST RANDOM FOREST TRAINING - HANDLES ALL DATA TYPES")
print("=" * 80)

# Load dataset
csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'afriwork.csv')
df = pd.read_csv(csv_path)

print(f"\n📊 Loaded {len(df):,} records")
print(f"📋 Columns: {list(df.columns)}")

# Drop rows where Job_title is missing
df = df[df['Job_title'].notna()]
print(f"✅ After dropping missing job titles: {len(df):,} records")

features = []
targets = []
skipped = 0

# English and Amharic character detection
def contains_english(text):
    return bool(re.search(r'[a-zA-Z]', str(text)))

def extract_english_words(text):
    return re.findall(r'[a-zA-Z]+', str(text))

print("\n🔧 Processing records...")

for idx, row in df.iterrows():
    try:
        job_title = str(row.get('Job_title', '')).strip()
        job_type = str(row.get('Job_type', '')).strip() if pd.notna(row.get('Job_type')) else ''
        sector = str(row.get('sector', '')).strip() if pd.notna(row.get('sector')) else ''
        location = str(row.get('location', '')).strip() if pd.notna(row.get('location')) else ''
        experience = str(row.get('Experience_level', '')).strip() if pd.notna(row.get('Experience_level')) else ''
        description = str(row.get('description', '')).strip() if pd.notna(row.get('description')) else ''
        
        if not job_title or len(job_title) < 2:
            skipped += 1
            continue
        
        title_lower = job_title.lower()
        has_english = contains_english(title_lower)
        
        # Extract English words for better matching
        english_words = extract_english_words(title_lower)
        
        # Simple but effective features
        feature = {
            # Basic title features
            'title_length': min(len(job_title), 100),
            'title_word_count': len(job_title.split()),
            'has_english': 1 if has_english else 0,
            
            # Seniority indicators
            'has_senior': 1 if 'senior' in title_lower or 'sr' in title_lower else 0,
            'has_junior': 1 if 'junior' in title_lower or 'jr' in title_lower or 'entry' in title_lower else 0,
            'has_lead': 1 if any(x in title_lower for x in ['lead', 'manager', 'head', 'supervisor', 'director']) else 0,
            'has_assistant': 1 if 'assistant' in title_lower or 'aide' in title_lower else 0,
            
            # Technology keywords
            'has_developer': 1 if any(x in title_lower for x in ['developer', 'engineer', 'programmer', 'coder']) else 0,
            'has_python': 1 if 'python' in title_lower else 0,
            'has_javascript': 1 if any(x in title_lower for x in ['javascript', 'js', 'react', 'angular', 'vue', 'node']) else 0,
            'has_java': 1 if 'java' in title_lower else 0,
            'has_sql': 1 if any(x in title_lower for x in ['sql', 'database', 'mysql', 'postgres']) else 0,
            'has_web': 1 if any(x in title_lower for x in ['web', 'frontend', 'backend', 'full stack']) else 0,
            
            # Business keywords
            'has_sales': 1 if any(x in title_lower for x in ['sales', 'marketing', 'business', 'bd']) else 0,
            'has_accounting': 1 if any(x in title_lower for x in ['accountant', 'accounting', 'finance', 'cashier', 'audit', 'tax']) else 0,
            'has_hr': 1 if any(x in title_lower for x in ['hr', 'human resources', 'recruitment', 'talent']) else 0,
            'has_admin': 1 if any(x in title_lower for x in ['admin', 'secretary', 'reception', 'office', 'assistant']) else 0,
            'has_manager': 1 if 'manager' in title_lower or 'management' in title_lower else 0,
            
            # Healthcare keywords
            'has_medical': 1 if any(x in title_lower for x in ['nurse', 'doctor', 'medical', 'health', 'clinical', 'patient', 'hospital']) else 0,
            
            # Education keywords
            'has_teaching': 1 if any(x in title_lower for x in ['teacher', 'instructor', 'professor', 'trainer', 'tutor']) else 0,
            
            # Amharic keywords (based on character patterns)
            'has_amharic': 1 if not has_english and len(title_lower) > 3 else 0,
            
            # Job type features
            'is_remote': 1 if 'remote' in job_type.lower() or 'work from home' in job_type.lower() else 0,
            'is_fulltime': 1 if 'full' in job_type.lower() or 'permanent' in job_type.lower() else 0,
            'is_parttime': 1 if 'part' in job_type.lower() or 'hourly' in job_type.lower() else 0,
            'is_contract': 1 if 'contract' in job_type.lower() or 'temporary' in job_type.lower() else 0,
            
            # Sector features
            'is_tech_sector': 1 if 'technology' in str(sector).lower() or 'it' in str(sector).lower() else 0,
            'is_finance_sector': 1 if 'finance' in str(sector).lower() or 'bank' in str(sector).lower() else 0,
            'is_health_sector': 1 if 'health' in str(sector).lower() or 'medical' in str(sector).lower() else 0,
            
            # Location features
            'is_addis': 1 if 'addis' in location.lower() else 0,
            'is_remote_location': 1 if 'remote' in location.lower() or 'anywhere' in location.lower() else 0,
            
            # Experience features
            'exp_senior': 1 if 'senior' in experience.lower() or '5+' in experience else 0,
            'exp_mid': 1 if 'mid' in experience.lower() or '3-5' in experience else 0,
            'exp_entry': 1 if 'entry' in experience.lower() or 'junior' in experience.lower() or '1-2' in experience else 0,
            
            # Description features
            'desc_length': min(len(description), 500) if description else 0,
            'desc_has_description': 1 if len(description) > 50 else 0,
        }
        
        features.append(feature)
        
        # Determine target category with simple logic
        title_lower = job_title.lower()
        
        # Technology category
        tech_keywords = ['developer', 'engineer', 'programmer', 'software', 'it', 'python', 'java', 'javascript', 'react', 
                        'angular', 'sql', 'database', 'web', 'app', 'mobile', 'android', 'ios', 'data', 'cloud', 'devops']
        
        # Finance category
        finance_keywords = ['accountant', 'finance', 'cashier', 'audit', 'tax', 'bank', 'accounting', 'bookkeeper', 'payroll']
        
        # Healthcare category
        health_keywords = ['nurse', 'doctor', 'medical', 'health', 'clinical', 'patient', 'hospital', 'care']
        
        # Education category
        education_keywords = ['teacher', 'instructor', 'professor', 'trainer', 'tutor', 'school', 'university']
        
        # Business category
        business_keywords = ['sales', 'marketing', 'manager', 'business', 'hr', 'admin', 'secretary', 'reception', 'officer', 'coordinator']
        
        # Calculate scores
        tech_score = sum(1 for kw in tech_keywords if kw in title_lower)
        finance_score = sum(1 for kw in finance_keywords if kw in title_lower)
        health_score = sum(1 for kw in health_keywords if kw in title_lower)
        education_score = sum(1 for kw in education_keywords if kw in title_lower)
        business_score = sum(1 for kw in business_keywords if kw in title_lower)
        
        scores = {
            'Technology': tech_score,
            'Finance': finance_score,
            'Healthcare': health_score,
            'Education': education_score,
            'Business': business_score
        }
        
        max_score = max(scores.values())
        if max_score > 0:
            target = max(scores, key=scores.get)
        else:
            # Check sector for hints
            if 'technology' in str(sector).lower() or 'it' in str(sector).lower():
                target = 'Technology'
            elif 'finance' in str(sector).lower() or 'bank' in str(sector).lower():
                target = 'Finance'
            elif 'health' in str(sector).lower():
                target = 'Healthcare'
            elif 'education' in str(sector).lower():
                target = 'Education'
            else:
                target = 'General'
        
        targets.append(target)
        
        # Progress indicator
        if (idx + 1) % 5000 == 0:
            print(f"   Processed {idx + 1:,} records...")
            
    except Exception as e:
        skipped += 1
        continue

print(f"\n✅ Processed {len(features):,} valid job records")
print(f"⚠️ Skipped: {skipped} invalid records")

if len(features) == 0:
    print("\n❌ No valid records found!")
    exit()

# Create DataFrame
X = pd.DataFrame(features)
y = pd.Series(targets)

print(f"\n📊 Feature matrix shape: {X.shape}")
print(f"📋 Total features: {len(X.columns)}")

print(f"\n🎯 Target distribution:")
for category, count in y.value_counts().items():
    pct = (count / len(y)) * 100
    bar = '█' * int(pct / 2)
    print(f"   {category:12} : {count:6,} ({pct:5.1f}%) {bar}")

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
print("   This may take 3-5 minutes...")

rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced',
    verbose=0
)

rf_model.fit(X_train, y_train)

# Evaluate
y_pred = rf_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n{'='*60}")
print(f"📊 MODEL PERFORMANCE")
print(f"{'='*60}")
print(f"   ✅ Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"   📚 Training samples: {len(X_train):,}")
print(f"   🧪 Test samples: {len(X_test):,}")

# Cross-validation
print(f"\n📊 5-Fold Cross-Validation:")
cv_scores = cross_val_score(rf_model, X_scaled, y_encoded, cv=5, n_jobs=-1)
print(f"   Mean CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")

# Per-category accuracy
print(f"\n📊 Per-Category Performance:")
print(f"{'='*60}")
report = classification_report(y_test, y_pred, target_names=label_encoder.classes_, output_dict=True)
for category in label_encoder.classes_:
    if category in report:
        prec = report[category]['precision']
        rec = report[category]['recall']
        f1 = report[category]['f1-score']
        print(f"   {category:12} - Precision: {prec:.3f}, Recall: {rec:.3f}, F1: {f1:.3f}")

# Feature importance
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

print(f"\n📈 TOP 15 IMPORTANT FEATURES:")
print(f"{'='*60}")
for i, row in feature_importance.head(15).iterrows():
    bar_length = int(row['importance'] * 50)
    bar = '█' * bar_length
    print(f"   {row['feature']:20} : {row['importance']:.4f} {bar}")

# Save model
model_path = "ml_models/"
if not os.path.exists(model_path):
    os.makedirs(model_path)

with open(f"{model_path}ethiopian_job_rf_model.pkl", "wb") as f:
    pickle.dump(rf_model, f)
with open(f"{model_path}ethiopian_rf_scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)
with open(f"{model_path}ethiopian_rf_encoder.pkl", "wb") as f:
    pickle.dump(label_encoder, f)

print(f"\n{'='*60}")
print(f"🎉 MODEL TRAINING COMPLETE!")
print(f"{'='*60}")
print(f"   ✅ Model saved to: {model_path}ethiopian_job_rf_model.pkl")
print(f"   📊 Final Accuracy: {accuracy*100:.2f}%")
print(f"   🔧 Features used: {len(X.columns)}")
print(f"   📁 Training data: {len(X):,} records")
print(f"   🎯 Categories: {len(label_encoder.classes_)}")
print(f"{'='*60}")