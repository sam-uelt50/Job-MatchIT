echo from ml_career_integration import career_ml > test_ml.py
echo print("=" * 50) >> test_ml.py
echo print("TESTING THE TRAINED MODEL") >> test_ml.py
echo print("=" * 50) >> test_ml.py
echo print("\n1. Similar jobs to Software Engineer:") >> test_ml.py
echo similar = career_ml.find_similar_jobs("Software Engineer", 5) >> test_ml.py
echo if similar: >> test_ml.py
echo     for job in similar: >> test_ml.py
echo         print(f"   -> {job['title']} ({job['similarity']}% match)") >> test_ml.py
echo else: >> test_ml.py
echo     print("   No similar jobs found") >> test_ml.py
echo print("\n2. Career path from Junior Developer:") >> test_ml.py
echo path = career_ml.predict_career_path("Junior Developer", 5) >> test_ml.py
echo if path: >> test_ml.py
echo     for step in path: >> test_ml.py
echo         print(f"   -> {step['title']} (confidence: {step['confidence']}%)") >> test_ml.py
echo else: >> test_ml.py
echo     print("   No career path found") >> test_ml.py
echo print("\n" + "=" * 50) >> test_ml.py
echo print("Test complete!") >> test_ml.py