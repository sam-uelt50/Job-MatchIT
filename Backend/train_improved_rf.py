# backend/train_improved_rf.py
from random_forest_matcher_improved import improved_rf

def train():
    print("=" * 60)
    print("🌲 Training IMPROVED Random Forest Model")
    print("=" * 60)
    
    success = improved_rf.train_model()
    
    if success:
        print("\n✅ Improved Random Forest model trained!")
        
        # Test
        print("\n🧪 Testing predictions:")
        test_cases = [
            ("Senior Python Developer", "Full-time", "Technology", "Addis Ababa", "Senior"),
            ("Junior Accountant", "Full-time", "Finance", "Remote", "Entry"),
            ("React Developer", "Remote", "Technology", "Remote", "Mid"),
            ("Sales Manager", "Full-time", "Business", "Addis Ababa", "Senior"),
        ]
        
        for title, jtype, sector, loc, exp in test_cases:
            result = improved_rf.predict_category(title, jtype, sector, loc, exp)
            if result:
                print(f"\n   Job: {title}")
                print(f"   Predicted: {result['category']} (Confidence: {result['confidence']}%)")
    else:
        print("\n⚠️ Training failed")

if __name__ == "__main__":
    train()