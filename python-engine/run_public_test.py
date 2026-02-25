import pandas as pd
from core import commit_dataset

# 1. Fetching a small, publicly available text corpus
print("Downloading public text corpus (SMS Spam Collection)...")
url = "https://raw.githubusercontent.com/justmarkham/DAT8/master/data/sms.tsv"
df = pd.read_csv(url, sep='\t', header=None, names=['label', 'text'])

# Save it locally
df.to_csv("public_dataset.csv", index=False)
print(f"Downloaded {len(df)} rows of text data.\n")

# 2. Commit Version 1 (Raw Data)
print("Committing Version 1 (Raw)...")
hash1 = commit_dataset(
    raw_filepath="public_dataset.csv", 
    text_col="text", 
    config={"lowercase": False, "deduplicate": False}
)

# 3. Commit Version 2 (Cleaned Data)
print("Committing Version 2 (Cleaned)...")
hash2 = commit_dataset(
    raw_filepath="public_dataset.csv", 
    text_col="text", 
    config={"lowercase": True, "deduplicate": True}
)

# 4. Commit Version 3 (Significant Shift: High-Length Filter)
# This will significantly reduce the row count and change the vocab size.
print("Committing Version 3 (Aggressive Filtering - Long Messages Only)...")
hash3 = commit_dataset(
    raw_filepath="public_dataset.csv", 
    text_col="text", 
    config={
        "lowercase": True, 
        "deduplicate": True, 
        "filter_short": True, 
        "min_length": 50  # Filter out all messages under 50 characters
    }
)

print(f"\nSUCCESS! 3 Versions created.")
print(f"Version 1 (Raw): {hash1}")
print(f"Version 2 (Cleaned): {hash2}")
print(f"Version 3 (Filtered): {hash3}")
print("\nNow Refresh your DVS Sidebar in VS Code to see Version 3!")