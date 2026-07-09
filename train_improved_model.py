import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import pickle

print("=" * 60)
print("TRAINING IMPROVED RANDOM FOREST MODEL")
print("=" * 60)

# Load dataset
df = pd.read_csv('Career_Path_Dataset_with_Career.csv')
print(f"✅ Loaded {len(df)} records")

# Combine features
text_columns = [col for col in df.columns if 'skill' in col.lower() or 'education' in col.lower() or 'interest' in col.lower()]
if not text_columns:
    text_columns = [col for col in df.columns if col not in ['Suggested Career Path', 'Career Path']]

df['combined'] = ''
for col in text_columns:
    df['combined'] += df[col].fillna('').astype(str) + " "

# Find target
target_col = 'Suggested Career Path' if 'Suggested Career Path' in df.columns else df.columns[0]
for col in df.columns:
    if 'career' in col.lower() or 'path' in col.lower():
        target_col = col
        break

print(f"🎯 Target: {target_col}")

# Vectorize
vectorizer = TfidfVectorizer(max_features=1000, stop_words='english', ngram_range=(1, 2))
X = vectorizer.fit_transform(df['combined'])

# Encode
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(df[target_col])

print(f"📊 Features: {X.shape[1]}, Classes: {len(label_encoder.classes_)}")

# Train with better parameters
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("\n🤖 Training Improved Random Forest...")
rf_model = RandomForestClassifier(
    n_estimators=300,        # More trees
    max_depth=20,            # Deeper trees
    min_samples_split=10,    # Prevent overfitting
    min_samples_leaf=4,      # More samples per leaf
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train, y_train)

# Cross-validation
cv_scores = cross_val_score(rf_model, X, y, cv=5)
print(f"📊 Cross-validation accuracy: {cv_scores.mean() * 100:.2f}% (+/- {cv_scores.std() * 100:.2f}%)")

# Test accuracy
y_pred = rf_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"📊 Test accuracy: {accuracy * 100:.2f}%")

# Save
model_data = {
    'model': rf_model,
    'vectorizer': vectorizer,
    'label_encoder': label_encoder
}

with open(r'C:\Users\Samuel\OneDrive\Desktop\JOB RECRUIMENT AND RECOMMEND\Backend\career_match_model.pkl', 'wb') as f:
    pickle.dump(model_data, f)

print("\n💾 Model saved!")

# Test prediction with confidence
def predict_with_confidence(text):
    vec = vectorizer.transform([text])
    pred = rf_model.predict(vec)[0]
    career = label_encoder.inverse_transform([pred])[0]
    probs = rf_model.predict_proba(vec)[0]
    confidence = max(probs) * 100
    return career, confidence

test_texts = [
    "Computer Science graduate, Python, Java, Machine Learning, AI",
    "Business administration degree, marketing, sales, leadership",
    "Civil engineering, AutoCAD, project management, construction"
]

print("\n🧪 TEST PREDICTIONS:")
for text in test_texts:
    career, conf = predict_with_confidence(text)
    print(f"   Input: {text[:40]}...")
    print(f"   → {career} (Confidence: {conf:.1f}%)\n")

print("✅ Training complete!")