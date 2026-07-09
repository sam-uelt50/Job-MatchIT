
# backend/train_rf_model.py
from random_forest_matcher import rf_matcher

def train_model():
    print("=" * 60)
    print("🌲 Training Random Forest Model")
    print("=" * 60)
    
    success = rf_matcher.train_model()
    
    if success:
        print("\n✅ Random Forest model trained successfully!")
    else:
        print("\n⚠️ Training failed")
    
    return success

if __name__ == "__main__":
    train_model()