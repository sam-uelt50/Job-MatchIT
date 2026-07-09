import pandas as pd
import numpy as np
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
import re
import os

print("=" * 60)
print("TRAINING ML MODEL ON DATASET")
print("=" * 60)

DB_PATH = r'C:\Users\Samuel\OneDrive\Desktop\JOB RECRUIMENT AND RECOMMEND\Backend\job_recruitment.db'

# Load data from database
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT id, title, required_skills, experience_required, industry FROM jobs WHERE required_skills IS NOT NULL", conn)
conn.close()

print(f"✓ Loaded {len(df)} jobs from database")

# Create TF-IDF vectorizer for skills
vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
skill_vectors = vectorizer.fit_transform(df['required_skills'].fillna(''))

print(f"✓ Created {skill_vectors.shape[1]} skill features")

# Features and target
X = skill_vectors.toarray()
y = df['experience_required'].values

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"\n📊 Training Data:")
print(f"   Training samples: {len(X_train)}")
print(f"   Testing samples: {len(X_test)}")

# Train Random Forest model
print("\n🤖 Training Random Forest Classifier...")
rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    random_state=42,
    n_jobs=-1
)

rf_model.fit(X_train, y_train)

# Evaluate
y_pred = rf_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n✅ Model Accuracy: {accuracy * 100:.2f}%")

# Save model
model_data = {
    'model': rf_model,
    'vectorizer': vectorizer,
    'feature_names': vectorizer.get_feature_names_out().tolist()
}

model_path = r'C:\Users\Samuel\OneDrive\Desktop\JOB RECRUIMENT AND RECOMMEND\Backend\professional_match_model.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(model_data, f)

print(f"\n💾 Model saved to: {model_path}")

# Test prediction function
def predict_experience(skills_text):
    """Predict required experience based on skills"""
    skill_vec = vectorizer.transform([skills_text])
    prediction = rf_model.predict(skill_vec.toarray())[0]
    return prediction

# Test with sample skills
test_skills = "Python, JavaScript, React, SQL"
predicted_exp = predict_experience(test_skills)
print(f"\n🧪 Test Prediction:")
print(f"   Skills: {test_skills}")
print(f"   Predicted experience requirement: {predicted_exp} years")

print("\n✅ ML Model training complete!")