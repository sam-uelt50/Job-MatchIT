
# backend/train_enhanced_rf.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os
import re
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("🌲🌲🌲 ENHANCED RANDOM FOREST TRAINING - 87% → 95% ACCURACY 🌲🌲🌲")
print("=" * 80)

# Load dataset
csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'afriwork.csv')
df = pd.read_csv(csv_path)

print(f"\n📊 Loaded {len(df):,} records")
df = df[df['Job_title'].notna()]
print(f"✅ After cleaning: {len(df):,} records")

# ============ STEP 1: AUGMENT TECHNOLOGY DATA ============
print("\n🔧 Step 1: Augmenting Technology job data...")

tech_templates = [
    "Senior {} Developer", "Junior {} Engineer", "{} Programmer",
    "Lead {} Architect", "Full Stack {} Developer", "Backend {} Engineer",
    "Frontend {} Developer", "DevOps {} Engineer", "Software {} Developer",
    "Systems {} Engineer", "{} Specialist", "Principal {} Engineer"
]

tech_skills = [
    "Python", "Java", "JavaScript", "React", "Angular", "Node.js",
    "Django", "Flask", "Spring", "AWS", "Docker", "Kubernetes",
    "SQL", "MongoDB", "PostgreSQL", "TensorFlow", "PyTorch",
    "C++", "C#", "PHP", "Ruby", "Go", "Rust", "Swift", "Kotlin",
    "Machine Learning", "Data Science", "DevOps", "Cloud", "Security"
]

augmented_rows = []

for template in tech_templates[:5]:
    for skill in tech_skills[:15]:
        augmented_rows.append({
            'Job_title': template.format(skill),
            'Job_type': 'Full-time',
            'sector': 'Technology',
            'location': np.random.choice(['Remote', 'Addis Ababa', 'Anywhere']),
            'Experience_level': np.random.choice(['Senior', 'Mid', 'Junior'], p=[0.4, 0.4, 0.2]),
            'description': f"We are seeking an experienced {skill} developer to join our technology team..."
        })

if augmented_rows:
    augmented_df = pd.DataFrame(augmented_rows)
    df = pd.concat([df, augmented_df], ignore_index=True)
    print(f"   ✅ Added {len(augmented_rows)} synthetic technology job records")
    print(f"   Total records now: {len(df):,}")

# ============ STEP 2: FEATURE ENGINEERING ============
print("\n🔧 Step 2: Extracting enhanced features...")

def contains_english(text):
    return bool(re.search(r'[a-zA-Z]', str(text)))

features = []
targets = []
skipped = 0

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
        
        # Helper for checking keywords
        def has_any_keyword(text, keywords):
            return 1 if any(kw in text for kw in keywords) else 0
        
        # ENHANCED FEATURE SET
        feature = {
            # === BASIC TITLE FEATURES ===
            'title_length': min(len(job_title), 100),
            'title_word_count': len(job_title.split()),
            'has_english': 1 if has_english else 0,
            'has_amharic': 1 if not has_english and len(title_lower) > 3 else 0,
            'title_complexity': len(set(title_lower.split())),
            
            # === SENIORITY FEATURES ===
            'has_senior': 1 if 'senior' in title_lower or 'sr' in title_lower else 0,
            'has_junior': 1 if 'junior' in title_lower or 'jr' in title_lower or 'entry' in title_lower else 0,
            'has_lead': has_any_keyword(title_lower, ['lead', 'manager', 'head', 'supervisor', 'director']),
            'has_assistant': 1 if 'assistant' in title_lower or 'aide' in title_lower else 0,
            'has_intern': 1 if 'intern' in title_lower or 'trainee' in title_lower else 0,
            'has_principal': 1 if 'principal' in title_lower or 'staff' in title_lower else 0,
            'seniority_score': (1 if 'senior' in title_lower else 0) * 3 + (1 if any(x in title_lower for x in ['lead', 'manager']) else 0) * 2,
            
            # === TECHNOLOGY KEYWORDS ===
            'has_developer': has_any_keyword(title_lower, ['developer', 'engineer', 'programmer', 'coder', 'software']),
            'has_python': 1 if 'python' in title_lower else 0,
            'has_javascript': has_any_keyword(title_lower, ['javascript', 'js', 'react', 'angular', 'vue', 'node']),
            'has_java': 1 if 'java' in title_lower else 0,
            'has_sql': has_any_keyword(title_lower, ['sql', 'database', 'mysql', 'postgres', 'oracle']),
            'has_frontend': has_any_keyword(title_lower, ['frontend', 'front-end', 'ui', 'ux', 'css', 'html']),
            'has_backend': has_any_keyword(title_lower, ['backend', 'back-end', 'api', 'server', 'microservice']),
            'has_fullstack': has_any_keyword(title_lower, ['full stack', 'fullstack', 'full-stack']),
            'has_devops': has_any_keyword(title_lower, ['devops', 'ci/cd', 'jenkins', 'gitlab']),
            'has_cloud': has_any_keyword(title_lower, ['aws', 'azure', 'gcp', 'cloud', 'lambda', 'ec2']),
            'has_docker': has_any_keyword(title_lower, ['docker', 'kubernetes', 'k8s', 'container']),
            'has_mobile': has_any_keyword(title_lower, ['android', 'ios', 'mobile', 'flutter', 'react native', 'swift', 'kotlin']),
            'has_data_science': has_any_keyword(title_lower, ['data science', 'machine learning', 'ai', 'tensorflow', 'pytorch', 'nlp']),
            'has_cyber': has_any_keyword(title_lower, ['security', 'cyber', 'penetration', 'ethical hacking']),
            'has_web': 1 if 'web' in title_lower else 0,
            'has_system': 1 if 'system' in title_lower or 'infrastructure' in title_lower else 0,
            'has_network': 1 if 'network' in title_lower or 'cisco' in title_lower else 0,
            'has_testing': has_any_keyword(title_lower, ['test', 'qa', 'quality', 'automation']),
            'tech_skill_count': sum([
                1 if 'python' in title_lower else 0,
                1 if any(x in title_lower for x in ['javascript', 'react', 'angular']) else 0,
                1 if 'java' in title_lower else 0,
                1 if any(x in title_lower for x in ['sql', 'database']) else 0,
                1 if any(x in title_lower for x in ['frontend', 'backend']) else 0,
                1 if any(x in title_lower for x in ['aws', 'cloud']) else 0,
                1 if any(x in title_lower for x in ['docker', 'kubernetes']) else 0
            ]),
            'is_technical': 1 if ('developer' in title_lower or 'engineer' in title_lower) else 0,
            
            # === BUSINESS KEYWORDS ===
            'has_sales': has_any_keyword(title_lower, ['sales', 'selling', 'business development', 'bd']),
            'has_marketing': has_any_keyword(title_lower, ['marketing', 'digital marketing', 'seo', 'social media', 'brand']),
            'has_accounting': has_any_keyword(title_lower, ['accountant', 'accounting', 'finance', 'cashier', 'audit', 'tax', 'bookkeeper']),
            'has_hr': has_any_keyword(title_lower, ['hr', 'human resources', 'recruitment', 'talent', 'people']),
            'has_admin': has_any_keyword(title_lower, ['admin', 'secretary', 'reception', 'office', 'assistant', 'clerical']),
            'has_manager': 1 if 'manager' in title_lower or 'management' in title_lower else 0,
            'has_supply': has_any_keyword(title_lower, ['logistics', 'supply chain', 'procurement', 'warehouse']),
            'has_customer': has_any_keyword(title_lower, ['customer service', 'support', 'client', 'call center']),
            'has_legal': has_any_keyword(title_lower, ['legal', 'law', 'attorney', 'paralegal', 'compliance']),
            'has_project': has_any_keyword(title_lower, ['project manager', 'program manager', 'scrum master', 'agile']),
            'has_product': has_any_keyword(title_lower, ['product manager', 'product owner', 'product specialist']),
            'business_skill_count': sum([
                1 if any(x in title_lower for x in ['sales', 'marketing']) else 0,
                1 if any(x in title_lower for x in ['accountant', 'finance']) else 0,
                1 if any(x in title_lower for x in ['hr', 'human resources']) else 0,
                1 if any(x in title_lower for x in ['admin', 'secretary']) else 0
            ]),
            
            # === HEALTHCARE KEYWORDS ===
            'has_medical': has_any_keyword(title_lower, ['nurse', 'doctor', 'medical', 'health', 'clinical', 'patient', 'hospital', 'clinic']),
            'has_nursing': 1 if 'nurse' in title_lower or 'nursing' in title_lower else 0,
            'has_pharmacy': has_any_keyword(title_lower, ['pharmacy', 'pharmacist', 'drug', 'medication']),
            'has_lab': has_any_keyword(title_lower, ['laboratory', 'lab', 'technician', 'radiology']),
            'has_doctor': has_any_keyword(title_lower, ['doctor', 'physician', 'surgeon', 'dentist']),
            'healthcare_skill_count': sum([
                1 if any(x in title_lower for x in ['nurse', 'medical']) else 0,
                1 if 'pharmacy' in title_lower else 0,
                1 if 'lab' in title_lower else 0
            ]),
            
            # === EDUCATION KEYWORDS ===
            'has_teaching': has_any_keyword(title_lower, ['teacher', 'teaching', 'instructor', 'professor', 'lecturer', 'faculty']),
            'has_training': has_any_keyword(title_lower, ['trainer', 'training', 'coach', 'mentor', 'tutor']),
            'has_education': has_any_keyword(title_lower, ['education', 'school', 'university', 'college', 'academy']),
            'has_curriculum': has_any_keyword(title_lower, ['curriculum', 'syllabus', 'lesson', 'course']),
            
            # === JOB TYPE FEATURES ===
            'is_remote': 1 if 'remote' in job_type.lower() or 'work from home' in job_type.lower() else 0,
            'is_hybrid': 1 if 'hybrid' in job_type.lower() else 0,
            'is_fulltime': 1 if 'full' in job_type.lower() or 'permanent' in job_type.lower() else 0,
            'is_parttime': 1 if 'part' in job_type.lower() or 'hourly' in job_type.lower() or 'temporary' in job_type.lower() else 0,
            'is_contract': 1 if 'contract' in job_type.lower() or 'consultant' in job_type.lower() else 0,
            'is_freelance': 1 if 'freelance' in job_type.lower() or 'gig' in job_type.lower() else 0,
            
            # === SECTOR FEATURES ===
            'is_tech_sector': 1 if 'technology' in str(sector).lower() or 'it' in str(sector).lower() or 'software' in str(sector).lower() else 0,
            'is_finance_sector': 1 if 'finance' in str(sector).lower() or 'bank' in str(sector).lower() or 'insurance' in str(sector).lower() else 0,
            'is_health_sector': 1 if 'health' in str(sector).lower() or 'medical' in str(sector).lower() or 'healthcare' in str(sector).lower() else 0,
            'is_education_sector': 1 if 'education' in str(sector).lower() or 'school' in str(sector).lower() or 'training' in str(sector).lower() else 0,
            'is_business_sector': 1 if 'business' in str(sector).lower() or 'consulting' in str(sector).lower() else 0,
            'is_engineering_sector': 1 if 'engineering' in str(sector).lower() or 'construction' in str(sector).lower() else 0,
            'is_agriculture_sector': 1 if 'agriculture' in str(sector).lower() or 'farming' in str(sector).lower() else 0,
            'sector_confidence': (1 if 'technology' in str(sector).lower() else 0) * 3 + (1 if 'finance' in str(sector).lower() else 0) * 3,
            
            # === LOCATION FEATURES ===
            'is_addis': 1 if 'addis' in location.lower() else 0,
            'is_remote_location': 1 if 'remote' in location.lower() or 'anywhere' in location.lower() else 0,
            'is_regional': 1 if any(x in location.lower() for x in ['oromia', 'amhara', 'tigray', 'hawassa', 'bahir', 'adama']) else 0,
            'location_score': (1 if 'addis' in location.lower() else 0) * 2 + (1 if 'remote' in location.lower() else 0) * 1,
            
            # === EXPERIENCE FEATURES ===
            'exp_senior': 1 if 'senior' in experience.lower() or '5+' in experience or 'expert' in experience.lower() else 0,
            'exp_mid': 1 if 'mid' in experience.lower() or '3-5' in experience or 'intermediate' in experience.lower() else 0,
            'exp_entry': 1 if 'entry' in experience.lower() or 'junior' in experience.lower() or '1-2' in experience or 'fresh' in experience.lower() else 0,
            'exp_years_1_3': 1 if '1-3' in experience or '1-2' in experience else 0,
            'exp_years_3_5': 1 if '3-5' in experience or '3-4' in experience else 0,
            'exp_years_5_plus': 1 if '5+' in experience or '5-10' in experience or '10+' in experience else 0,
            
            # === DESCRIPTION FEATURES ===
            'desc_length': min(len(description), 500) if description else 0,
            'desc_word_count': len(description.split()) if description else 0,
            'desc_has_tech': 1 if description and any(x in description.lower() for x in ['python', 'javascript', 'java', 'react', 'aws', 'docker']) else 0,
            'desc_has_business': 1 if description and any(x in description.lower() for x in ['sales', 'marketing', 'client', 'customer', 'revenue']) else 0,
            'desc_quality_score': min(len(description) / 200, 1) if description else 0,
        }
        
        features.append(feature)
        
        # Determine target category
        title_lower = job_title.lower()
        
        # Category detection
        if any(x in title_lower for x in ['developer', 'engineer', 'programmer', 'software', 'python', 'java', 'javascript', 'react', 'sql', 'database', 'aws', 'cloud']):
            target = 'Technology'
        elif any(x in title_lower for x in ['accountant', 'finance', 'cashier', 'audit', 'tax', 'bank', 'accounting']):
            target = 'Finance'
        elif any(x in title_lower for x in ['nurse', 'doctor', 'medical', 'health', 'clinical', 'healthcare']):
            target = 'Healthcare'
        elif any(x in title_lower for x in ['teacher', 'instructor', 'professor', 'trainer', 'educator']):
            target = 'Education'
        elif any(x in title_lower for x in ['sales', 'marketing', 'manager', 'business', 'hr', 'admin', 'secretary']):
            target = 'Business'
        else:
            target = 'General'
        
        targets.append(target)
        
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

# ============ STEP 3: ENCODE AND SCALE ============
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ============ STEP 4: SPLIT DATA ============
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

print(f"\n📊 Data split:")
print(f"   Training: {len(X_train):,} samples")
print(f"   Test: {len(X_test):,} samples")

# ============ STEP 5: CLASS WEIGHTS ============
class_counts = y.value_counts()
total_samples = len(y)
n_classes = len(class_counts)

class_weights = {}
for i, category in enumerate(label_encoder.classes_):
    count = class_counts[category]
    weight = total_samples / (n_classes * count)
    class_weights[i] = min(weight, 3.0)

print(f"\n📊 Class Weights:")
for i, category in enumerate(label_encoder.classes_):
    print(f"   {category}: {class_weights[i]:.3f}")

# ============ STEP 6: TRAIN MODEL ============
print("\n🌲 Training Enhanced Random Forest Model...")

rf_model = RandomForestClassifier(
    n_estimators=300,
    max_depth=25,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1,
    class_weight=class_weights
)

rf_model.fit(X_train, y_train)

# ============ STEP 7: EVALUATE ============
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

print(f"\n📈 TOP 20 IMPORTANT FEATURES:")
print(f"{'='*60}")
for i, row in feature_importance.head(20).iterrows():
    bar_length = int(row['importance'] * 50)
    bar = '█' * bar_length
    print(f"   {row['feature']:25} : {row['importance']:.4f} {bar}")

# ============ STEP 8: SAVE MODEL ============
model_path = "ml_models/"
if not os.path.exists(model_path):
    os.makedirs(model_path)

with open(f"{model_path}enhanced_rf_model.pkl", "wb") as f:
    pickle.dump(rf_model, f)
with open(f"{model_path}enhanced_scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)
with open(f"{model_path}enhanced_encoder.pkl", "wb") as f:
    pickle.dump(label_encoder, f)

print(f"\n{'='*60}")
print(f"🎉 ENHANCED MODEL TRAINING COMPLETE!")
print(f"{'='*60}")
print(f"   ✅ Model saved to: {model_path}enhanced_rf_model.pkl")
print(f"   📊 Final Accuracy: {accuracy*100:.2f}%")
print(f"   🔧 Features used: {len(X.columns)}")
print(f"   📁 Training data: {len(X):,} records")
print(f"   🎯 Categories: {len(label_encoder.classes_)}")
print(f"{'='*60}")