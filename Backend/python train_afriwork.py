# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import re
import os

print("=" * 60)
print("TRAINING JOB MATCHING MODEL WITH AFRIWORK DATA")
print("=" * 60)

# Check if file exists
if not os.path.exists('afriwork.csv'):
    print("afriwork.csv not found!")
    exit(1)

# Load data
df = pd.read_csv('afriwork.csv')
print(f"Loaded {len(df):,} job postings")

# Clean and prepare job titles
def clean_title(title):
    if pd.isna(title):
        return ""
    title = str(title)
    title = re.sub(r'[^\w\s]', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    return title.lower()

df['clean_title'] = df['Job_title'].apply(clean_title)
df = df[df['clean_title'] != ""]
df = df[df['clean_title'].str.len() > 2]

# Get unique job titles
unique_titles = df['clean_title'].unique()
print(f"Unique job titles: {len(unique_titles):,}")

# Create TF-IDF vectorizer
print("Creating TF-IDF vectorizer...")
vectorizer = TfidfVectorizer(
    analyzer='char', 
    ngram_range=(2, 5), 
    max_features=1000,
    lowercase=True
)
job_vectors = vectorizer.fit_transform(unique_titles)
print(f"Vector shape: {job_vectors.shape}")

# Save models
print("Saving models...")
with open('ethiopian_job_vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)
with open('ethiopian_job_vectors.pkl', 'wb') as f:
    pickle.dump(job_vectors, f)
with open('ethiopian_job_titles.pkl', 'wb') as f:
    pickle.dump(list(unique_titles), f)
print(f"Saved model with {len(unique_titles):,} job titles")

# Test the model
print("\nTESTING MODEL:")
test_jobs = ['accountant', 'sales', 'graphics designer', 'driver', 'teacher']

for test_job in test_jobs:
    test_vec = vectorizer.transform([test_job])
    similarities = cosine_similarity(test_vec, job_vectors)[0]
    top_indices = similarities.argsort()[-6:][::-1]
    
    print(f"\nSimilar jobs to '{test_job}':")
    count = 0
    for idx in top_indices:
        if similarities[idx] > 0.15 and count < 5:
            print(f"   -> {unique_titles[idx]} ({similarities[idx]*100:.1f}%)")
            count += 1
    if count == 0:
        print("   No similar jobs found")

print("\n" + "=" * 60)
print("Training complete! Model saved.")
print("=" * 60)