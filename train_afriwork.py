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

if not os.path.exists('afriwork.csv'):
    print("afriwork.csv not found!")
    exit(1)

df = pd.read_csv('afriwork.csv')
print(f"Loaded {len(df):,} job postings")

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

unique_titles = df['clean_title'].unique()
print(f"Unique job titles: {len(unique_titles):,}")

vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2,5), max_features=1000)
job_vectors = vectorizer.fit_transform(unique_titles)

with open('ethiopian_job_vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)
with open('ethiopian_job_vectors.pkl', 'wb') as f:
    pickle.dump(job_vectors, f)
with open('ethiopian_job_titles.pkl', 'wb') as f:
    pickle.dump(list(unique_titles), f)

print(f"Saved model with {len(unique_titles):,} job titles")
print("Training complete!")