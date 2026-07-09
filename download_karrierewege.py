# download_karrierewege.py
from datasets import load_dataset
import pandas as pd
import os

print("=" * 70)
print("DOWNLOADING KARRIEREWEGE DATASET (2.48 MILLION CAREER PATHS)")
print("=" * 70)

# Load the dataset
print("\n📥 Loading dataset from Hugging Face...")
print("   This may take 5-10 minutes (1GB download)...")

dataset = load_dataset("ElenaSenger/Karrierewege", trust_remote_code=True)

print(f"\n✅ Dataset loaded successfully!")
print(f"\n📊 Dataset splits:")
for split_name, split_data in dataset.items():
    print(f"   - {split_name}: {len(split_data):,} rows")

# Save to CSV (optional - takes time for 2M rows)
print("\n💾 Saving to CSV files...")

# Save training split (1.98M rows) - this will take time
train_df = pd.DataFrame(dataset['train'])
train_df.to_csv('karrierewege_train.csv', index=False)
print(f"   ✓ Saved: karrierewege_train.csv ({len(train_df):,} rows)")

# Save validation split
val_df = pd.DataFrame(dataset['validation'])
val_df.to_csv('karrierewege_validation.csv', index=False)
print(f"   ✓ Saved: karrierewege_validation.csv ({len(val_df):,} rows)")

# Save test split
test_df = pd.DataFrame(dataset['test'])
test_df.to_csv('karrierewege_test.csv', index=False)
print(f"   ✓ Saved: karrierewege_test.csv ({len(test_df):,} rows)")

print("\n✅ Download complete! Ready for training.")