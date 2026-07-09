import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import pickle
import os

print("=" * 60)
print("TRAINING ML MODEL WITH CAREER PATH DATASET")
print("=" * 60)

# Load the dataset
df = pd.read_csv('Career_Path_Dataset_with_Career.csv')
print(f"✅ Loaded {len(df)} records")

# Show column names (to understand the data)
print(f"\n📋 Columns in dataset:")
for col in df.columns:
    print(f"   - {col}")

# Create combined features from all relevant text columns
# (Adjust column names based on actual dataset)
text_columns = []
for col in df.columns:
    if col.lower() not in ['suggested career path', 'career path', 'target', 'id']:
        text_columns.append(col)

print(f"\n📊 Using {len(text_columns)} columns for features")

# Combine all text columns
df['combined_features'] = ''
for col in text_columns:
    df['combined_features'] += df[col].fillna('').astype(str) + " "

# Find the target column (career path)
target_col = None
for col in df.columns:
    if 'career' in col.lower() or 'path' in col.lower() or 'suggested' in col.lower():
        target_col = col
        break

if target_col:
    print(f"🎯 Target column: {target_col}")
    df = df[df[target_col].notna()]
else:
    print("❌ Could not find target column")
    exit()

# Create TF-IDF vectors
vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
X = vectorizer.fit_transform(df['combined_features'])

# Encode target labels
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(df[target_col])

print(f"\n📊 Feature matrix: {X.shape}")
print(f"📊 Unique career paths: {len(label_encoder.classes_)}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
print("\n🤖 Training Random Forest...")
rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
rf_model.fit(X_train, y_train)

# Evaluate
y_pred = rf_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\n✅ Model Accuracy: {accuracy * 100:.2f}%")

# Save model
model_data = {
    'model': rf_model,
    'vectorizer': vectorizer,
    'label_encoder': label_encoder,
    'feature_names': vectorizer.get_feature_names_out().tolist()
}

model_path = r'C:\Users\Samuel\OneDrive\Desktop\JOB RECRUIMENT AND RECOMMEND\Backend\career_match_model.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(model_data, f)

print(f"\n💾 Model saved to: {model_path}")

# Test prediction
def predict_career(profile_text):
    features = vectorizer.transform([profile_text])
    pred = rf_model.predict(features)[0]
    career = label_encoder.inverse_transform([pred])[0]
    prob = max(rf_model.predict_proba(features)[0]) * 100
    return career, prob

test_profile = "Computer Science graduate with Python, Java skills interested in AI"
career, confidence = predict_career(test_profile)
print(f"\n🧪 Test: '{test_profile[:50]}...'")
print(f"   Predicted Career: {career}")
print(f"   Confidence: {confidence:.1f}%")

print("\n✅ Training complete!")