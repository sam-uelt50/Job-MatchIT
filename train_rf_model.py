# backend/train_rf_model.py
from random_forest_matcher import rf_matcher

def train_model():
    print("=" * 60)
    print("🌲 Training Random Forest Model")
    print("=" * 60)
    
    success = rf_matcher.train_model()
    
    if success:
        print("\n✅ Random Forest model trained successfully!")
        
        # Test prediction
        print("\n🧪 Testing predictions:")
        test_cases = [
            ("Senior Python Developer", "Full-time", "Technology", "Addis Ababa", "Senior"),
            ("Junior Accountant", "Full-time", "Finance", "Remote", "Entry"),
            ("React Developer", "Remote", "Technology", "Remote", "Mid"),
            ("Sales Manager", "Full-time", "Business", "Addis Ababa", "Senior"),
            ("Nurse", "Full-time", "Healthcare", "Hawassa", "Mid"),
        ]
        
        for title, jtype, sector, loc, exp in test_cases:
            result = rf_matcher.predict_job_category(title, jtype, sector, loc, exp)
            print(f"\n   Job: {title}")
            print(f"   Predicted: {result['predicted_category']} (Confidence: {result['confidence']}%)")
            print(f"   Top predictions: {result['top_predictions']}")
    else:
        print("\n❌ Training failed")
    
    return success

if __name__ == "__main__":
    train_model()